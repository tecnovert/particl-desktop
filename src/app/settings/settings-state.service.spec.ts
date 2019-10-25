import { TestBed, inject } from '@angular/core/testing';

import { CoreModule } from 'app/core/core.module';

import { SettingsStateService } from './settings-state.service';
import { RpcWithStateModule } from 'app/core/rpc/rpc.module';
import { MultiwalletModule } from 'app/multiwallet/multiwallet.module';

describe('SettingsStateService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        RpcWithStateModule.forRoot(),
        CoreModule.forRoot(),
        MultiwalletModule.forRoot()
      ],
      providers: [SettingsStateService]
    });
  });

  it('should be created', inject([SettingsStateService], (service: SettingsStateService) => {
    expect(service).toBeTruthy();
  }));
});
