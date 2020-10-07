import { Observable } from 'rxjs';
import { PriceItem, ORDER_ITEM_STATUS, ESCROW_TYPE, BID_DATA_KEY } from '../../shared/market.models';


export interface GenericOrderModalInputs {
  orderItem: OrderItem;
}


export interface OrderModalResponse {
  doAction: boolean;
  params: ActionTransitionParams;
}


export interface OrderItem {
  orderId: number;
  orderItemId: number;
  orderHash: string;
  baseBidId: number;
  marketKey: string;
  created: number;
  updated: number;
  listing?: {
    title: string;
    image: string;
    id: number;
    hash: string;
    hashPrefix: string;
  };
  pricing?: {
    basePrice: PriceItem;
    shippingPrice: PriceItem;
    subTotal: PriceItem;
    escrowAmount: PriceItem;
    totalRequired: PriceItem;
  };
  shippingDetails?: {
    name: string;
    addressLine1: string;
    addressLine2: string;
    city: string;
    state: string;
    code: string;
    country: string;
  };
  contactDetails?: {
    phone: string;
    email: string;
  };
  currentState?: BuyflowStateDetails;
  extraDetails?: {
    escrowMemo: string;
    shippingMemo: string;
    releaseMemo: string;
    escrowTxn: string;
    releaseTxn: string;
    rejectionReason: string;
  };
}


export type OrderUserType = 'BUYER' | 'SELLER';

export type BuyFlowType = ESCROW_TYPE | 'UNSUPPORTED';

export type BuyFlowOrderType = ORDER_ITEM_STATUS | 'UNKNOWN';

export enum StateStatusClass {
  NONE = '',
  PRIMARY = 'primary',
  SECONDARY = 'secondary',
  TERTIARY = 'tertiary',
  ALERT = 'alert',
  WARNING = 'warning',
  WARNING_OTHER = 'warning-alt',
  INACTIVE = 'inactive'
}


// We're not creating a state machine for each and every order. Instead, we create a single state machine for each buyflow type,
//  and then provides methods to lookup the current state ad actions, for each order. More like a workflow than a state machine...
export interface IBuyflowController {
  getOrderedStateList(buyflow: BuyFlowType): BuyFlowState[];
  getStateDetails(buyflow: BuyFlowType, stateId: BuyFlowOrderType, user: OrderUserType): BuyflowStateDetails;
  actionOrderItem(orderItem: OrderItem, toState: BuyFlowOrderType, asUser: OrderUserType): Observable<OrderItem>;
}

export type BuyFlowStore = {
  [buyflow in BuyFlowType]?: BuyFlow;
};

export interface BuyFlow {
  states: BuyFlowStateStore;
  actions: BuyFlowActionStore;
}

export type BuyFlowStateStore = {
  [state in BuyFlowOrderType]?: BuyFlowState
};

export interface BuyFlowState {
  buyflow: BuyFlowType;
  stateId: BuyFlowOrderType;
  label: string;
  filterLabel?: string;
  order: number;
  stateInfo: {
    buyer: string;
    seller: string;
  };
  statusClass: StateStatusClass;
}

type BuyflowActionType = 'PRIMARY' | 'ALTERNATIVE' | 'PLACEHOLDER_LABEL';

export type ActionTransitionParams = {
  [key in BID_DATA_KEY.DELIVERY_EMAIL | BID_DATA_KEY.DELIVERY_PHONE | 'memo']?: string;
};

export type BuyFlowActionStore = {
  [fromState in BuyFlowOrderType]?: BuyflowAction[];
};

export interface BuyflowAction {
  fromState: BuyFlowOrderType;
  toState: BuyFlowOrderType | null;
  user: OrderUserType;
  actionType: BuyflowActionType;
  details: {
    label: string;
    tooltip: string;
    colour: 'primary' | 'warn';
    icon: string;
  };
  transition(orderItem: OrderItem, extraParams: ActionTransitionParams): Observable<boolean>;
}


export interface BuyflowStateDetails {
  state: BuyFlowState;
  actions: { [actionType in BuyflowActionType]: BuyflowAction[] };
}
