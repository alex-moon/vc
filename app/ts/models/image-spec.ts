export class ImageSpec {
    texts: string[] = [];
    styles: string[] = [];
    iterations ?: number;
    upscale ?: boolean;
}

export class VideoStepSpec extends ImageSpec {
    init_iterations ?: number;
    epochs ?: number;
    x_velocity ?: number;
    y_velocity ?: number;
    z_velocity ?: number;
}
