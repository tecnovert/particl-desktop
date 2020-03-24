import { Identity } from './market.models';


export namespace MarketActions {

  export class StartMarketService {
    static readonly type: string = '[Market] Start Market Service';
  }

  export class StopMarketService {
    static readonly type: string = '[Market] Stop Market Service';
  }


  export class LoadIdentities {
    static readonly type: string = '[Market] Load Identities';
  }

  export class SetCurrentIdentity {
    static readonly type: string = '[Market] Set Current Identity';
    constructor(public identity: Identity) {}
  }
}
