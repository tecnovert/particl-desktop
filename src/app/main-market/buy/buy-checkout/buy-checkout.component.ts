import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material';

import { ListingDetailModalComponent } from '../../shared/listing-detail-modal/listing-detail-modal.component';
import { PlaceBidModalComponent } from './place-bid-modal/place-bid-modal.component';

@Component({
  selector: 'market-buy-checkout',
  templateUrl: './buy-checkout.component.html',
  styleUrls: ['./buy-checkout.component.scss']
})
export class BuyCheckoutComponent implements OnInit {

  saveShippingProfile: boolean = false;

  constructor(
    private _dialog: MatDialog
  ) { }

  ngOnInit() {
  }


  openListingDetailModal(): void {
    const dialog = this._dialog.open(ListingDetailModalComponent);
  }

  openPlaceBidModal(): void {
    const dialog = this._dialog.open(PlaceBidModalComponent);
  }

}
