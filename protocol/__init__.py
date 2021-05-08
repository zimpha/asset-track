#!/usr/bin/env python3

class YieldFarmingBase(object):
    @property
    def type(self):
        return 'Farming'

    @property
    def name(self):
        raise NotImplementedError

    @property
    def share_decimals(self):
        return 18

    @staticmethod
    def pool_name(original_token_name, underlying_protocol=None):
        raise NotImplementedError

    def staked(self, user, pool_name, block_number='latest', optimizer=None):
        raise NotImplementedError

    def reward(self, user, pool_name, block_number='latest'):
        raise NotImplementedError

    def apy(self, pool_name):
        raise NotImplementedError


class LendingBase(YieldFarmingBase):
    @property
    def type(self):
        return 'Lending'

    def supply(self, user, pool_name, block_number='latest', optimizer=None):
        raise NotImplementedError

    def borrow(self, user, pool_name, block_number='latest'):
        raise NotImplementedError

    def supply_interest_rate(self, user, pool_name, block_number='latest'):
        raise NotImplementedError

    def borrow_interest_rate(self, user, pool_name, block_number='latest'):
        raise NotImplementedError

    def borrow_reward(self, user, pool_name, block_number='latest'):
        raise NotImplementedError
    
    def supply_reward(self, user, pool_name, block_number='latest'):
        raise NotImplementedError

    def supply_apy(self, user, pool_name, block_number='latest'):
        raise NotImplementedError

    def borrow_apy(self, user, pool_name, block_number='latest'):
        raise NotImplementedError

    def supply_value(self, user, block_number='latest'):
        raise NotImplementedError

    def borrow_value(self, user, block_number='latest'):
        raise NotImplementedError
