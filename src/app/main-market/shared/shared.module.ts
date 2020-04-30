import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TreeSelectComponent } from './tree-select/tree-select.component';
import { CoreUiModule } from 'app/core-ui/core-ui.module';
import { QuestionAnswerThreadComponent } from './question-answer-thread/question-answer-thread.component';
import { OrderListItemComponent } from './order-list-item/order-list-item.component';
import { ListingListItemComponent } from './listing-list-item/listing-list-item.component';


@NgModule({
  imports: [
    CommonModule,
    CoreUiModule
  ],
  declarations: [
    TreeSelectComponent,
    QuestionAnswerThreadComponent,
    OrderListItemComponent,
    ListingListItemComponent
  ],
  exports: [
    TreeSelectComponent,
    QuestionAnswerThreadComponent,
    OrderListItemComponent,
    ListingListItemComponent
  ],
  entryComponents: [
  ],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class MarketSharedModule { }

export { TreeSelectComponent } from './tree-select/tree-select.component';
