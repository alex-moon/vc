/**
 * @see https://github.com/Unaxiom/unnotify
 * Modifications have been made to this file
 *
   Copyright 2021 Pratheek Adidela

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
 */

"use strict";
exports.__esModule = true;
var notificationCenter;
var notificationCenterClassName = "unnotify-center";
var eachNotificationClassName = "unnotify-panel";
var notificationButtonClassName = "unnotify-button";
var defaultTimeout = 5000;
/**Creates and appends the stylesheet to the document */
function __unnotifyCreateStyleSheet(localNotificationCenterClassName, localEachNotificationClassName, notificationButtonClassName, side, clickable) {
    if (side === undefined || side === null) {
        side = "right";
    }
    else if (side === 'left') {
        side = 'left';
    }
    else {
        side = 'right';
    }
    var notificationCenterStyle = document.createElement("style");
    notificationCenterStyle.type = "text/css";
    notificationCenterStyle.innerHTML = __unnotifyReturnClasses(localNotificationCenterClassName, localEachNotificationClassName, notificationButtonClassName, side, clickable);
    document.getElementsByTagName('head')[0].appendChild(notificationCenterStyle);
    // Create the notification center
    notificationCenter = document.createElement("div");
    notificationCenter.classList.add(localNotificationCenterClassName);
    // document.body.appendChild(notificationCenter);
    document.body.insertBefore(notificationCenter, document.body.firstChild);
}
/**Returns the required classes */
function __unnotifyReturnClasses(localNotificationCenterClassName, localEachNotificationClassName, localNotificationButtonClassName, side, clickable) {
    var pointerEvents = "initial";
    if (!clickable) {
        pointerEvents = "none";
    }
    return "\n        ." + localNotificationCenterClassName + " {\n            position: absolute;\n            top: 20px;\n            z-index: 25000;\n            overflow-y: auto;\n            overflow-x: hidden;\n            pointer-events: " + pointerEvents + ";\n        }\n\n        ." + localEachNotificationClassName + " {\n            padding: 10px;\n            margin: 10px;\n            border-radius: 8px;\n            color: #fff;\n            width: 350px;\n            min-height: 40px;\n            position: static;\n            top: 30px;\n            z-index: 25100;\n            pointer-events: " + pointerEvents + ";\n        }\n\n        ." + localNotificationButtonClassName + " {\n            float: right;\n            position: relative;\n            top: -7px;\n            right: -10px;\n            background-color: transparent;\n            border: none;\n            pointer-events: initial;\n        }\n\n        .unnotify-close-btn {\n            color: #fff;\n            cursor: pointer;\n        }\n\n        .unnotify-action-btn {\n            width: 50%;\n            color: #fff;\n            text-align: center;\n            padding: 5px 0px;\n            margin-top: 10px;\n            border: none;\n            cursor: pointer;\n            background-color: rgba(0, 0, 0, 0);\n            outline: none;\n        }\n\n        .unnotify-action-btn:hover {\n            background-color: rgba(0, 0, 0, 0.1);\n            outline: none;\n        }\n\n        .unnotify-input {\n            background-color: rgba(0, 0, 0, 0.2);\n            width: 100%;\n            margin: 5px 0px;\n            padding: 5px 0px;\n            text-align: center;\n            color: #fff;\n            border-top-style: hidden;\n            border-right-style: hidden;\n            border-left-style: hidden;\n            border-bottom-style: hidden;\n        }\n\n        .unnotify-success {\n            background-color: rgba(27, 94, 32, 0.8);\n        }\n\n        .unnotify-info {\n            background-color: rgba(29, 121, 198, 0.8);\n        }\n\n        .unnotify-warning {\n            background-color: rgba(251, 114, 4, 0.8);\n        }\n\n        .unnotify-danger {\n            background-color: rgba(213, 0, 0, 0.8);\n        }\n\n        /* Custom, iPhone Retina */ \n        @media only screen and (min-width : 320px) {\n            ." + localNotificationCenterClassName + " {\n                margin: 0px 2px;\n                padding: 0px 2px;\n            }\n\n            ." + localEachNotificationClassName + " {\n                width: 300px;\n            }\n        }\n    \n        /* Extra Small Devices, Phones */ \n        @media only screen and (min-width : 480px) {\n            ." + localNotificationCenterClassName + " {\n                width: 360px;\n                " + side + ": 0px;\n                padding: 0px 10px;\n                margin: 0px 20px;\n            }\n\n            ." + localEachNotificationClassName + " {\n                width: 90%;\n            }\n        }\n    \n        /* Small Devices, Tablets */\n        @media only screen and (min-width : 768px) {\n            ." + localNotificationCenterClassName + " {\n                width: 360px;\n                " + side + ": 0px;\n                padding: 0px 10px;\n                margin: 0px 20px;\n            }\n\n            ." + localEachNotificationClassName + " {\n                width: 90%;\n            }\n        }\n    ";
}
/**Returns a random ID */
function randomID() {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}
/**Returns the Div Element that houses the notification */
function __unnotifyDiv(eachNotificationClassName, options) {
    var div = document.createElement("div");
    div.id = randomID();
    div.classList.add(eachNotificationClassName);
    if (options.type == "success" || options.type == "info" || options.type == "danger" || options.type == "warning") {
        div.classList.add("unnotify-" + options.type);
    }
    else if (typeof (options.customClass) != "undefined" || typeof (options.customClass) != null || options.customClass != "") {
        div.classList.add(options.customClass);
    }
    if (typeof (options.animateIn) != "undefined") {
        div.classList.add("animated");
        div.classList.add(options.animateIn);
        div.setAttribute("data-animate-in", options.animateIn);
    }
    else {
        div.setAttribute("data-animate-in", "");
    }
    if (typeof (options.animateOut) != "undefined") {
        div.setAttribute("data-animate-out", options.animateOut);
    }
    else {
        div.setAttribute("data-animate-out", "");
    }
    return div;
}
/**Returns the title div */
function __unnotifyTitle(title) {
    var titleDiv = document.createElement("div");
    var titleSpan = document.createElement("span");
    titleSpan.style.fontWeight = "700";
    titleSpan.style.fontSize = "larger";
    titleSpan.innerText = title;
    titleDiv.appendChild(titleSpan);
    return titleDiv;
}
/**Returns the button which would close the notification */
function __unnotifyCloseButton(closeButtonClass) {
    var closeButton = document.createElement("button");
    closeButton.classList.add(closeButtonClass);
    closeButton.classList.add("unnotify-close-btn");
    closeButton.classList.add("material-icons");
    closeButton.innerText = "close";
    return closeButton;
}
function __unnotifyActionButton(text) {
    var btn = document.createElement("button");
    btn.classList.add("unnotify-action-btn");
    btn.innerText = text;
    return btn;
}
/**Returns the div that displays the content of the notification */
function __unnotifyContent(content) {
    var contentDiv = document.createElement("div");
    contentDiv.innerHTML = content;
    return contentDiv;
}
function __setupDestroyEventHandlers(div, options) {
    // If timeout is 0, then don't autodestroy it
    if (typeof (options.timeout) == "undefined" || typeof (options.timeout) == null || options.timeout < 0) {
        setTimeout(function () {
            destroy(div.id);
        }, defaultTimeout);
    }
    else if (options.timeout > 0) {
        setTimeout(function () {
            destroy(div.id);
        }, options.timeout);
    }
}
/**Internal function to display the notification */
function __unnotifyShow(eachNotificationClassName, notificationButtonClassName, title, content, options) {
    var div = __unnotifyDiv(eachNotificationClassName, options);
    var titleDiv = __unnotifyTitle(title);
    var closeButton = __unnotifyCloseButton(notificationButtonClassName);
    titleDiv.appendChild(closeButton);
    closeButton.addEventListener('click', function () {
        destroy(div.id);
    });
    var contentDiv = __unnotifyContent(content);
    div.appendChild(titleDiv);
    div.appendChild(contentDiv);
    __setupDestroyEventHandlers(div, options);
    notificationCenter.appendChild(div);
    return div.id;
}
/**Internal function to display a confirmation notification */
function __unnotifyConfirm(eachNotificationClassName, notificationButtonClassName, content, options, confirmButtonName, cancelButtonName, onConfirmCallback, onCancelCallback) {
    var div = __unnotifyDiv(eachNotificationClassName, options);
    var closeButton = __unnotifyCloseButton(notificationButtonClassName);
    closeButton.addEventListener('click', function () {
        destroy(div.id);
    });
    var contentDiv = __unnotifyContent(content);
    var confirmButton = __unnotifyActionButton(confirmButtonName);
    var cancelButton = __unnotifyActionButton(cancelButtonName);
    div.appendChild(closeButton);
    div.appendChild(contentDiv);
    div.appendChild(confirmButton);
    div.appendChild(cancelButton);
    if (onConfirmCallback != undefined && onConfirmCallback != null) {
        confirmButton.addEventListener('click', function (evt) {
            onConfirmCallback(evt, div.id);
        });
    }
    if (onCancelCallback != undefined && onCancelCallback != null) {
        cancelButton.addEventListener('click', function (evt) {
            onCancelCallback(evt, div.id);
        });
    }
    notificationCenter.appendChild(div);
    return div.id;
}
/**Internal function to display an input notification */
function __unnotifyInputHandler(eachNotificationClassName, notificationButtonClassName, title, options, onNextCallback, onCancelCallback) {
    var div = __unnotifyDiv(eachNotificationClassName, options);
    var closeButton = __unnotifyCloseButton(notificationButtonClassName);
    closeButton.addEventListener('click', function () {
        destroy(div.id);
    });
    var titleDiv = __unnotifyContent(title);
    var inp = document.createElement("input");
    inp.id = randomID();
    inp.classList.add("unnotify-input");
    var confirmButton = __unnotifyActionButton("Next");
    var cancelButton = __unnotifyActionButton("Cancel");
    div.appendChild(closeButton);
    div.appendChild(titleDiv);
    div.appendChild(inp);
    div.appendChild(confirmButton);
    div.appendChild(cancelButton);
    if (onNextCallback != undefined && onNextCallback != null) {
        confirmButton.addEventListener('click', function (evt) {
            var valueEntered = inp.value;
            onNextCallback(evt, div.id, valueEntered);
        });
    }
    if (onCancelCallback != undefined && onCancelCallback != null) {
        cancelButton.addEventListener('click', function (evt) {
            onCancelCallback(evt, div.id);
        });
    }
    notificationCenter.appendChild(div);
    return div.id;
}
/**Internal function to destroy the notification with the given id */
function __unnotifyDestroy(id) {
    try {
        var div_1 = document.getElementById(id);
        // Apply the animate-out class
        var animateOut = div_1.getAttribute("data-animate-out");
        var animateIn = div_1.getAttribute("data-animate-in");
        if (animateOut.length != 0) {
            if (!div_1.classList.contains("animated")) {
                div_1.classList.add("animated");
            }
            if (animateIn.length != 0) {
                div_1.classList.remove(animateIn);
            }
            div_1.classList.add(animateOut);
            setTimeout(function () {
                div_1.parentNode.removeChild(div_1);
            }, 1000);
        }
        else {
            div_1.parentNode.removeChild(div_1);
        }
    }
    catch (e) { }
}
/**Initialises the notification module */
function init(side, clickable) {
    __unnotifyCreateStyleSheet(notificationCenterClassName, eachNotificationClassName, notificationButtonClassName, side, clickable);
}
exports.init = init;
/**Displays the notification and returns the ID of the notification element. Title is a string, content can either be a string or HTML. */
function show(title, content, options) {
    return __unnotifyShow(eachNotificationClassName, notificationButtonClassName, title, content, options);
}
exports.show = show;
/**Shows a confirmation notification (with two options: Confirm and Cancel) and accepts a confirmation callback (executed if the user confirms)
     * and an optional on-cancel callback (executed if the user cancels) and returns the ID of the notification */
function confirm(content, options, onConfirmCallback, onCancelCallback) {
    return __unnotifyConfirm(eachNotificationClassName, notificationButtonClassName, content, options, "Confirm", "Cancel", onConfirmCallback, onCancelCallback);
}
exports.confirm = confirm;
/**Shows a confirmation notification (with two options: Yes and No) and accepts a confirmation callback (executed if the user clicks on Yes)
    * and an optional callback that is executed if the user clicks on No, and returns the ID of the notification */
function affirm(content, options, onConfirmCallback, onCancelCallback) {
    return __unnotifyConfirm(eachNotificationClassName, notificationButtonClassName, content, options, "Yes", "No", onConfirmCallback, onCancelCallback);
}
exports.affirm = affirm;
/**Displays a notification with the provision for an input, which is passed to the onNextCallback when the user clicks on "Next" */
function input(title, options, onNextCallback, onCancelCallback) {
    return __unnotifyInputHandler(eachNotificationClassName, notificationButtonClassName, title, options, onNextCallback, onCancelCallback);
}
exports.input = input;
/**Destroys the notification with the associated ID */
function destroy(id) {
    __unnotifyDestroy(id);
}
exports.destroy = destroy;
/**Class that can display the notifications */
var Unnotify = /** @class */ (function () {
    /**Initialises everything. Accepts the side, whose dafault is right. Possible values are 'right', 'left' */
    function Unnotify(side, clickable) {
        this.localNotificationCenterClassName = notificationCenterClassName + "-" + side;
        this.localEachNotificationClassName = eachNotificationClassName + "-" + side;
        // Create the CSS rules required for the notification center
        __unnotifyCreateStyleSheet(this.localNotificationCenterClassName, this.localEachNotificationClassName, notificationButtonClassName, side, clickable);
    }
    /**Displays the notification and returns the ID of the notification element. Title is a string, content can either be a string or HTML. */
    Unnotify.prototype.show = function (title, content, options) {
        return __unnotifyShow(this.localEachNotificationClassName, notificationButtonClassName, title, content, options);
    };
    /**Shows a confirmation notification and accepts a confirmation callback (executed if the user confirms)
     * and an optional on-cancel callback (executed if the user cancels) and returns the ID of the notification */
    Unnotify.prototype.confirm = function (content, options, onConfirmCallback, onCancelCallback) {
        return __unnotifyConfirm(this.localEachNotificationClassName, notificationButtonClassName, content, options, "Confirm", "Cancel", onConfirmCallback, onCancelCallback);
    };
    /**Shows a confirmation notification (with two options: Yes and No) and accepts a confirmation callback (executed if the user clicks on Yes)
    * and an optional callback that is executed if the user clicks on No, and returns the ID of the notification */
    Unnotify.prototype.affirm = function (content, options, onConfirmCallback, onCancelCallback) {
        return __unnotifyConfirm(this.localEachNotificationClassName, notificationButtonClassName, content, options, "Yes", "No", onConfirmCallback, onCancelCallback);
    };
    /**Displays a notification with the provision for an input, which is passed to the onNextCallback when the user clicks on "Next" */
    Unnotify.prototype.input = function (title, options, onNextCallback, onCancelCallback) {
        return __unnotifyInputHandler(this.localEachNotificationClassName, notificationButtonClassName, title, options, onNextCallback, onCancelCallback);
    };
    /**Destroys the notification with the associated ID */
    Unnotify.prototype.destroy = function (id) {
        __unnotifyDestroy(id);
    };
    return Unnotify;
}());
exports.Unnotify = Unnotify;
