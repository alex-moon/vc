import {GenerationSpec} from "../models/generation-spec";
import {GenerationRequest} from "../models/generation-request";
import {ImageSpec} from "../models/image-spec";

export class ImageCounter {
    image = 0;
    text = 0;
    style = 0;

    constructor(private images: ImageSpec[]) {}

    next(): [string, string] {
        if (this.image >= this.images.length) {
            throw new Error('not enough image specs');
        }

        let image = this.images[this.image];

        if (this.text >= image.texts.length) {
            this.style = 0;
            this.text = 0;
            this.image ++;
            return this.next();
        }

        const text = image.texts[this.text];

        let style = null;
        if (image.styles.length) {
            if (this.style >= image.styles.length) {
                this.style = 0;
                this.text ++;
                return this.next();
            }
            style = image.styles[this.style];
            this.style ++;
        }

        return [text, style];
    }
}

export class Field {
    field: string;
    label: string;
    type: 'number'|'boolean';
    default: number|boolean;
    constructor(field: string, label: string, _default: number|boolean) {
        this.field = field;
        this.label = label;
        this.default = _default;
        this.type = typeof _default === 'boolean' ? 'boolean' : 'number';
    }
}

export class DetailsHelper {
    static getResultUrls(request: GenerationRequest) {
        const urls = [];
        for (const result of request.results) {
            if (result.url) {
                urls.push(result.url);
            } else if (result.url_watermarked) {
                urls.push(result.url_watermarked);
            }
        }
        if (!urls.length) {
            if (request.interim) {
                urls.push(request.interim);
            } else if (request.interim_watermarked) {
                urls.push(request.interim_watermarked);
            }
        }
        return urls;
    }

    static hasDetails(request: GenerationRequest) {
        return this.getResultUrls(request).length || request.spec instanceof GenerationSpec;
    }

    static getImageCounter(images: ImageSpec[]) {
        return new ImageCounter(images);
    }

    static getFields(video: boolean = false): Field[] {
        return video ? [
            new Field('init_iterations', 'init', 200.),
            new Field('iterations', 'iterations', 20),
            new Field('epochs', 'epochs', 42),
            new Field('transition', 'transition', 20),
            new Field('upscale', 'upscale', false),
            new Field('interpolate', 'interpolate', false),
            new Field('random_walk', 'walk', false),
            new Field('x_velocity', 'x', 0.),
            new Field('y_velocity', 'y', 0.),
            new Field('z_velocity', 'z', 0.),
            new Field('pan_velocity', 'pan', 0.),
            new Field('tilt_velocity', 'tilt', 0.),
            new Field('roll_velocity', 'roll', 0.),
        ] : [
            new Field('iterations', 'iterations', 200),
            new Field('upscale', 'upscale', false),
        ];
    }
}
