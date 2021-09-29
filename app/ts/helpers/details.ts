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
}
