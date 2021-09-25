import {GenerationSpec} from "../models/generation-spec";
import {GenerationRequest} from "../models/generation-request";

export class DetailsHelper {
    static getResultUrl(request: GenerationRequest) {
        for (const result of request.results) {
            if (result.url) {
                return result.url;
            }
            if (result.url_watermarked) {
                return result.url_watermarked;
            }
        }
        return request.interim || request.interim_watermarked;
    }

    static hasDetails(request: GenerationRequest) {
        return this.getResultUrl(request) !== null || request.spec instanceof GenerationSpec;
    }
}
