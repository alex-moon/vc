export class AuthHelper {
    private static token: string = null;
    private static callbacks: CallableFunction[] = [];
    private static authenticated = false;

    static getToken() {
        return AuthHelper.token;
    }

    static setToken(token: string) {
        AuthHelper.token = token
            || (new URLSearchParams(window.location.search)).get('token')
            || localStorage.getItem('vc-token');
    }

    static clearToken() {
        AuthHelper.token = null;
        AuthHelper.authenticated = false;
    }

    static authenticate() {
        AuthHelper.authenticated = true;
        localStorage.setItem('vc-token', AuthHelper.token);
        for (const callback of AuthHelper.callbacks) {
            callback(AuthHelper.token);
        }
    }

    static isAuthenticated() {
        return AuthHelper.authenticated;
    }

    static listen(callback: CallableFunction) {
        this.callbacks.push(callback);
    }
}
