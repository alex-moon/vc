import {GenerationSpec} from "../models/generation-spec";
import {GenerationRequest} from "../models/generation-request";

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
}
