from dacite import from_dict
from injector import inject

from vc.exception.tier_exception import TierException
from vc.manager import GenerationRequestManager
from vc.model.user import User
from vc.service.helper.steps import (
    Steps,
    ImageGenerationStep,
    VideoGenerationStep,
)
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

        if not TierHelper.is_artist(user) and steps > 800:
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
        self.spec(spec, user)

    def queued(self, user: User):
        if not TierHelper.is_god(user):
            queued = self.manager.mine_queued(user)
            if len(queued) > 0:
                raise TierException(
                    'God',
                    'Your tier is limited to one request at a time - '
                    'try cancelling an existing request first'
                )

    def spec(self, spec: GenerationSpec, user: User):
        if not TierHelper.is_artist(user):
            for step in Steps.iterate_steps(spec):
                if isinstance(step, ImageGenerationStep):
                    if step.spec.upscale:
                        raise TierException(
                            'Artist',
                            'Your tier is restricted from upscaling'
                        )
                if isinstance(step, VideoGenerationStep):
                    if step.upscaled:
                        raise TierException(
                            'Artist',
                            'Your tier is restricted from upscaling'
                        )
                    if step.interpolated:
                        raise TierException(
                            'Artist',
                            'Your tier is restricted from interpolation'
                        )
