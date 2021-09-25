export class AuthHelper {
    static token: string = null;
    static callbacks: CallableFunction[] = [];

    static setToken(token: string) {
        AuthHelper.token = token;
        for (const callback of AuthHelper.callbacks) {
            callback(token);
        }
    }

    static hasToken() {
        return AuthHelper.token !== null;
    }

    static listen(callback: CallableFunction) {
        this.callbacks.push(callback);
    }
}
