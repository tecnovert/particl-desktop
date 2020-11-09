import { Market } from '../services/data/data.models';

export enum StartedStatus {
  PENDING,
  STARTED,
  FAILED,
  STOPPED
}


export interface Profile {
  id: number;
  name: string;
}


export interface Identity {
  id: number;
  name: string;
  displayName: string;
  path: string;
  address: string;
  icon: string;
  carts: CartDetail[];
  markets: Market[];
}


export interface CartDetail {
  id: number;
  name: string;
}


export interface MarketSettings {
  port: number;
  defaultProfileID: number;
  defaultIdentityID: number;
  userRegion: string;
  canModifyIdentities: boolean;
  useAnonBalanceForFees: boolean;
  usePaidMsgForImages: boolean;
  startupWaitTimeoutSeconds: number;
  defaultListingCommentPageCount: number;
  daysToNotifyListingExpired: number;
}


export interface DefaultMarketConfig {
  url: string;
  imagePath: string;
  imageMaxSizeFree: number;
  imageMaxSizePaid: number;
}


export interface MarketNotifications {
  identityCartItemCount: number;
}


export interface MarketStateModel {
  started: StartedStatus;
  profile: Profile;
  identities: Identity[];
  identity: Identity;
  defaultConfig: DefaultMarketConfig;
  settings: MarketSettings;
  notifications: MarketNotifications;
}


// export interface ListingsCommentNotificationItem {
//   title: string;
//   imageId: number;
//   marketHash: string;
//   hasUnread: boolean;
// }


// export interface NotificationsStateModel {
//   listingComments:  {
//     buy: { [listingHash: string]: ListingsCommentNotificationItem }
//     sell: { [listingHash: string]: ListingsCommentNotificationItem }
//   };
// }
