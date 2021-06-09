import { xorWith, partition } from 'lodash';

import { State, StateToken, StateContext, Action, Selector, createSelector } from '@ngxs/store';
import { GovernanceStateActions } from './governance-store.actions';
import { GovernanceStateModel } from './governance-store.models';

import { ProposalItem } from './../base/governance.models';


const DEFAULT_STATE_TOKEN = new StateToken<GovernanceStateModel>('governance');

const DEFAULT_STATE_VALUES: GovernanceStateModel = {
  blockCount: 0,
  blockchainSynced: false,
  isPolling: false,
  lastRequestErrored: false,
  proposals: []
};


@State<GovernanceStateModel>({
  name: DEFAULT_STATE_TOKEN,
  defaults: JSON.parse(JSON.stringify(DEFAULT_STATE_VALUES))
})
export class GovernanceState {

  @Selector()
  static allProposals(state: GovernanceStateModel) {
    return state.proposals;
  }

  @Selector()
  static latestBlock(state: GovernanceStateModel) {
    return state.blockCount;
  }

  @Selector()
  static isBlocksSynced(state: GovernanceStateModel) {
    return state.blockchainSynced;
  }


  @Selector()
  static filteredProposals(state: GovernanceStateModel) {
    return  !state.blockchainSynced ?
            [[], []] :
            partition(
              state.proposals,
              p => ((p.blockStart === 0) && (p.blockEnd === 0)) || (p.blockEnd >= state.blockCount)
            );
  }


  static currentProposals() {
    return createSelector(
      [GovernanceState.filteredProposals],
      (filteredProposals: ProposalItem[][]): ProposalItem[] => {
        return filteredProposals[0] || [];
      }
    );
  }


  static previousProposals() {
    return createSelector(
      [GovernanceState.filteredProposals],
      (filteredProposals: ProposalItem[][]): ProposalItem[] => {
        return filteredProposals[1] || [];
      }
    );
  }


  /**
     * NB!!!! Once this state is loaded into the global store, it remains there permanently through the running of the application.
     * Which means:
     *
     * 1. Keep this as light-weight as possible:
     *    - do not store anything here that is not imperative for the general operation of this module;
     *    - make certain that there is exactly that which is needed (if certain circumstances require additional info, load it as needed);
     *    - if in doubt, don't store it;
     *    - ensure that there is nothing sensitive left in as part of the default store state.
     *
     * 2. If using ngxsOnInit(), remember that it is called only the first time the state is added to the global store!
     *    - So despite this module potentially being "loaded" multiple times (on each new init of the module),
     *      this function will only execute on the 1st load of the module.
     *    - for clean separation, we should be bootstrapping this module as another whole app inside the main application...
     *      We'll get to such a goal eventually... or at least that's the current forward direction.
     */

  constructor() {}


  @Action(GovernanceStateActions.ResetState)
  resetToDefaultState(ctx: StateContext<GovernanceStateModel>) {
    ctx.setState(JSON.parse(JSON.stringify(DEFAULT_STATE_VALUES)));
  }


  @Action(GovernanceStateActions.SetRetrieveFailedStatus)
  updateRequestFailedStatus(ctx: StateContext<GovernanceStateModel>, { status }: GovernanceStateActions.SetRetrieveFailedStatus) {
    ctx.patchState({ lastRequestErrored: !!status });
  }


  @Action(GovernanceStateActions.SetBlockValues)
  updateBlockStatusValues(ctx: StateContext<GovernanceStateModel>, { blockCount, percentComplete }: GovernanceStateActions.SetBlockValues) {
    if ((blockCount > 0) && (percentComplete > 0)) {
      ctx.patchState({ blockCount: blockCount, blockchainSynced: percentComplete >= 99});
    }
  }


  @Action(GovernanceStateActions.SetProposals)
  updateStoredProposals(ctx: StateContext<GovernanceStateModel>, { proposals }: GovernanceStateActions.SetProposals) {
    const currentState = ctx.getState();
    if (
      (currentState.proposals.length !== proposals.length) ||
      (xorWith<ProposalItem>(
        currentState.proposals,
        proposals,
        (curr, req) =>
            (curr.proposalId === req.proposalId) &&
            (curr.blockStart === req.blockStart) &&
            (curr.blockEnd === req.blockEnd)
      ).length > 0)
    ) {
      ctx.patchState({ proposals });
    }
  }

}
