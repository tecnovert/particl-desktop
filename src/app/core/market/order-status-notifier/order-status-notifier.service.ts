import { Injectable, OnDestroy } from '@angular/core';
import { Log } from 'ng2-logger';
import * as _ from 'lodash';

import { NotificationService } from 'app/core/notification/notification.service';
import { MarketStateService } from 'app/core/market/market-state/market-state.service';
import { ProfileService } from 'app/core/market/api/profile/profile.service';
import { Bid } from 'app/core/market/api/bid/bid.model';
import { take, takeWhile } from 'rxjs/operators';
import { Subscription } from 'rxjs';
import { SettingsStateService } from 'app/settings/settings-state.service';


class OrderSummary {

  data: any = {};

  private types: string[] = [
    'buy',
    'sell'
  ]

  constructor() {
    for (const type of this.types) {
      this.data[type] = {
        totalActive: 0,
        items: {}
      }
    }
  }
}
@Injectable()
export class OrderStatusNotifierService implements OnDestroy {

  log: any = Log.create('order-status-notifier.service id:' + Math.floor((Math.random() * 1000) + 1));

  private doNotify: boolean = true;
  private destroyed: boolean = false;
  private profileAddress: string = '';
  private activeOrders: OrderSummary = new OrderSummary();
  private notificationKey: string = 'timestamp_notifcation_orders';
  private orders$: Subscription;

  constructor(
    private _marketState: MarketStateService,
    private _notification: NotificationService,
    private profileService: ProfileService,
    private _settings: SettingsStateService
  ) {}

  public start() {
    this.log.d('order status notifier service started!');
    this.destroyed = false;
    this.loadOrders();

    this._settings.observe('settings.wallet.notifications.order_updated').pipe(
      takeWhile(() => !this.destroyed)
    ).subscribe(
      (isSubscribed) => {
        this.doNotify = Boolean(+isSubscribed);
      }
    );
  }

  public stop() {
    if (this.orders$) {
      this.orders$.unsubscribe();
    }
    this.destroyed = true;
  }

  public getActiveCount(type: string): number {
    return +((this.activeOrders.data[type] || {}).totalActive || 0);
  }

  private loadOrders() {
    this.profileService.default().pipe(take(1)).subscribe(
      (profile: any) => {
        this.profileAddress = String(profile.address);

        this.orders$ = this._marketState.observe('bid')
        .pipe(takeWhile(() => !this.destroyed)) // why are we not waiting for distinct updates only?
        .subscribe(bids => {
          const notifcationTimestamp = +(localStorage.getItem(this.notificationKey) || 0);
          const activeItems = new OrderSummary();

          for (const bid of bids) {
            let type: string;
            if (bid.ListingItem && (bid.ListingItem.seller  === this.profileAddress)) {
              type = 'sell';
            } else if (bid.bidder === this.profileAddress) {
              type = 'buy';
            }
            if (!type) {
              continue;
            }

            const order = new Bid(bid, type);
            const orderHash = order.ListingItem && order.ListingItem.hash.length ? order.ListingItem && order.ListingItem.hash : '';
            if (!orderHash.length) {
              continue;
            }

            if (!order.activeBuySell && !order.doNotify) {
              continue;
            }

            if (!_.isPlainObject(activeItems.data[type].items[orderHash])) {
              const title = order.ListingItem
                              && order.ListingItem.ItemInformation
                              && (typeof order.ListingItem.ItemInformation.title === 'string') ?
                              order.ListingItem.ItemInformation.title : orderHash;
              activeItems.data[type].items[orderHash] = {
                title: title,
                notificationCount: 0
              }
            }

            if (order.activeBuySell) {
              activeItems.data[type].totalActive += 1;
            }
            if (order.doNotify && +order.updatedAt > notifcationTimestamp) {
              activeItems.data[type].items[orderHash].notificationCount += 1;
            }
          };

          this.processUpdates(activeItems);
          this.activeOrders = activeItems;
        })
      }
    );
  }

  private processUpdates(newOrders: OrderSummary) {
    const newTypeKeys = Object.keys(newOrders.data);
    let hasUpdated = false;

    for (const typeKey of newTypeKeys) {
      const bidHashes = Object.keys(newOrders.data[typeKey].items);

      const count = bidHashes.reduce((total, hash) => total + +newOrders.data[typeKey].items[hash].notificationCount, 0);
      if (count > 0) {
        hasUpdated = true;
        if (this.doNotify) {
          const msg = `${count} ${typeKey} order(s) have been updated.`
          this.sendNotification(msg);
        }
      }
    }

    if (hasUpdated) {
      localStorage.setItem(this.notificationKey, String(Date.now()));
    }
  }

  private sendNotification(message: string) {
    this._notification.sendNotification(message);
  }

  ngOnDestroy() {
    this.destroyed = true;
  }

}
