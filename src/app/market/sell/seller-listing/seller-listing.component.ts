import { Component, Input, Output, EventEmitter } from '@angular/core';
import { MatDialog } from '@angular/material';
import { Router } from '@angular/router';
import { Log } from 'ng2-logger';

import { RpcStateService } from 'app/core/rpc/rpc-state/rpc-state.service';
import { TemplateService } from 'app/core/market/api/template/template.service';
import { ModalsHelperService } from 'app/modals/modals-helper.service';
import { SnackbarService } from 'app/core/snackbar/snackbar.service';

import { DeleteListingComponent } from '../../../modals/delete-listing/delete-listing.component';

import { Template } from 'app/core/market/api/template/template.model';
import { Listing } from 'app/core/market/api/listing/listing.model';
import { Status } from '../status.class';

@Component({
  selector: 'app-seller-listing',
  templateUrl: './seller-listing.component.html',
  styleUrls: ['./seller-listing.component.scss']
})
export class SellerListingComponent {

  @Output() onDelete: EventEmitter<any> = new EventEmitter();

  public status: Status = new Status();
  log: any = Log.create('seller-listing.component');

  @Input() listing: Listing;

  constructor(
    public dialog: MatDialog,
    private router: Router,
    private rpcState: RpcStateService,
    private modals: ModalsHelperService,
    private template: TemplateService,
    private snackbar: SnackbarService,
  ) {}

  getStatus(status: string) {
    return [this.status.get(status)];
  }

  confirmDeleteListing(template: Template): void {
    const dialogRef = this.dialog.open(DeleteListingComponent);
    dialogRef.componentInstance.templateToRemove = template;
    dialogRef.afterClosed().subscribe(
      () => this.onDelete.emit()
    );
  }

  // Triggered when the action button is clicked.
  action(listing: Listing) {
    switch (listing.status) {
      case 'unpublished':
        this.checkTemplateSize(listing);
        // this.postTemplate(listing);
        break;
      case 'awaiting':
      case 'published':
        break;
    }
  }

  checkTemplateSize(template: Template): void {
    this.template.size(template.id).subscribe(res => {
      if (res.fits) {
        this.postTemplate(template);
      } else {
        this.snackbar.open(`Upload Limit Exceeded ${res.imageData + res.spaceLeft}`);
      }
    }, error => {
      this.snackbar.open(error);
    })
  }

  postTemplate(template: Template) {
    this.modals.unlock({timeout: 30}, (status) => this.callTemplate(template));
  }

  async callTemplate(template: Template) {
    this.log.d('template', template)
    await this.template.post(template, 1, template.expireTime).toPromise();
  }
  // @TODO create a shared compoment
  addItem(id?: number, clone?: boolean) {
    this.router.navigate(['/market/template'], {
      queryParams: {'id': id, 'clone': clone }
    });
  }

}
