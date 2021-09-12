function GenerationRequest(raw=null) {
    if (raw) {
        Object.assign(this, raw);
    }
}
Object.assign(GenerationRequest.prototype, {
    // @todo not quite - you want to do this elsewhere
    marshall(formData) {
        for (let [key, value] of formData.entries()) {
            this[key] = value;
        }
    }
});
