export class ImageSpec {
    texts: string[] = [];
    styles: string[] = [];
    iterations ?: number;
    init_iterations ?: number;
    epochs ?: number;
    x_velocity ?: number;
    y_velocity ?: number;
    z_velocity ?: number;
    upscale ?: boolean;
}
