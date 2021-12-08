from dacite import from_dict
from injector import inject

from vc.exception.tier_exception import TierException
from vc.manager import GenerationRequestManager
from vc.model.user import User
from vc.service.helper.steps import Steps
from vc.service.helper.tier import TierHelper
from vc.value_object import GenerationSpec


class GenerationRequestValidator:
    manager: GenerationRequestManager

    @inject
    def __init__(self, manager: GenerationRequestManager):
        self.manager = manager

    def create(self, raw, user: User):
        spec = from_dict(
            data_class=GenerationSpec,
            data=raw['spec']
        )

        steps = Steps.total_steps(spec)

        if not TierHelper.is_coder(user):
            raise TierException('Coder')

        if steps > 800 and not TierHelper.is_artist(user):
            raise TierException(
                'Artist',
                'That spec would have %s steps - your tier is limited '
                'to 800 steps max' % steps
            )

        if not TierHelper.is_god(user) and steps > 1600:
            raise TierException(
                'God',
                'That spec would have %s steps - your tier is limited '
                'to 1600 steps max' % steps
            )

        self.queued(user)

    def queued(self, user: User):
        if not TierHelper.is_god(user):
            queued = self.manager.mine_queued(user)
            if len(queued) > 0:
                raise TierException(
                    'God',
                    'Your tier is limited to one request at a time - '
                    'try cancelling an existing request first'
                )
