from dataclasses import dataclass

from vc.value_object import ImageSpec, GenerationSpec


@dataclass
class GenerationStep:
    step: int


@dataclass
class ImageGenerationStep(GenerationStep):
    spec: ImageSpec
    text: str
    style: str = None
    video_step: int = None


@dataclass
class VideoGenerationStep(GenerationStep):
    upscaled: bool
    interpolated: bool


@dataclass
class HandleInterimStep(VideoGenerationStep):
    pass


@dataclass
class CleanFilesStep(GenerationStep):
    pass


class Steps:
    INTERIM_STEPS = 60

    @classmethod
    def iterate_steps(cls, spec: GenerationSpec):
        step = 0

        if spec.images:
            for step_spec in spec.images:
                if step_spec.texts:
                    for text in step_spec.texts:
                        if step_spec.styles:
                            for style in step_spec.styles:
                                step += 1
                                yield CleanFilesStep(step)
                                step += 1
                                yield ImageGenerationStep(
                                    spec=step_spec,
                                    step=step,
                                    text=text,
                                    style=style
                                )
                        else:
                            step += 1
                            yield CleanFilesStep(step)
                            step += 1
                            yield ImageGenerationStep(
                                spec=step_spec,
                                step=step,
                                text=text
                            )

        if spec.videos:
            for video in spec.videos:
                upscaled = False
                interpolated = False
                video_step = 0
                step += 1
                yield CleanFilesStep(step=step)
                if video.steps:
                    for step_spec in video.steps:
                        if step_spec.upscale:
                            upscaled = True
                        if step_spec.interpolate:
                            interpolated = True

                        if step_spec.texts:
                            for text in step_spec.texts:
                                if step_spec.styles:
                                    for style in step_spec.styles:
                                        for i in range(step_spec.epochs):
                                            video_step += 1
                                            step += 1
                                            yield ImageGenerationStep(
                                                spec=step_spec,
                                                step=step,
                                                text=text,
                                                style=style,
                                                video_step=video_step
                                            )

                                            if step % cls.INTERIM_STEPS == 1:
                                                step += 1
                                                yield HandleInterimStep(
                                                    step=step,
                                                    upscaled=upscaled,
                                                    interpolated=interpolated
                                                )
                                else:
                                    for i in range(step_spec.epochs):
                                        video_step += 1
                                        step += 1
                                        yield ImageGenerationStep(
                                            spec=step_spec,
                                            step=step,
                                            text=text,
                                            video_step=video_step
                                        )

                                        if step % cls.INTERIM_STEPS == 1:
                                            step += 1
                                            yield HandleInterimStep(
                                                step=step,
                                                upscaled=upscaled,
                                                interpolated=interpolated
                                            )

                step += 1
                yield VideoGenerationStep(
                    step=step,
                    upscaled=upscaled,
                    interpolated=interpolated
                )

    @classmethod
    def total_steps(cls, spec):
        steps_total = 0
        for _ in cls.iterate_steps(spec):
            steps_total += 1
        return steps_total

