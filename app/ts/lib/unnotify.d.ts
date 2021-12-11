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

/**Initialises the notification module */
export declare function init(side?: 'left' | 'right', clickable?: boolean): void;
/**Displays the notification and returns the ID of the notification element. Title is a string, content can either be a string or HTML. */
export declare function show(title: string, content: string, options: options): string;
/**Shows a confirmation notification (with two options: Confirm and Cancel) and accepts a confirmation callback (executed if the user confirms)
     * and an optional on-cancel callback (executed if the user cancels) and returns the ID of the notification */
export declare function confirm(content: string, options: options, onConfirmCallback: (evt: MouseEvent, id: string) => void, onCancelCallback?: (evt: MouseEvent, id: string) => void): string;
/**Shows a confirmation notification (with two options: Yes and No) and accepts a confirmation callback (executed if the user clicks on Yes)
    * and an optional callback that is executed if the user clicks on No, and returns the ID of the notification */
export declare function affirm(content: string, options: options, onConfirmCallback: (evt: MouseEvent, id: string) => void, onCancelCallback?: (evt: MouseEvent, id: string) => void): string;
/**Displays a notification with the provision for an input, which is passed to the onNextCallback when the user clicks on "Next" */
export declare function input(title: string, options: options, onNextCallback: (evt: MouseEvent, id: string, valueEntered: string) => void, onCancelCallback?: (evt: MouseEvent, id: string) => void): string;
/**Destroys the notification with the associated ID */
export declare function destroy(id: string): void;
/**Class that can display the notifications */
export declare class Unnotify {
    localNotificationCenterClassName: string;
    localEachNotificationClassName: string;
    /**Initialises everything. Accepts the side, whose dafault is right. Possible values are 'right', 'left' */
    constructor(side?: 'left' | 'right', clickable?: boolean);
    /**Displays the notification and returns the ID of the notification element. Title is a string, content can either be a string or HTML. */
    show(title: string, content: string, options: options): string;
    /**Shows a confirmation notification and accepts a confirmation callback (executed if the user confirms)
     * and an optional on-cancel callback (executed if the user cancels) and returns the ID of the notification */
    confirm(content: string, options: options, onConfirmCallback: (evt: MouseEvent, id: string) => void, onCancelCallback?: (evt: MouseEvent, id: string) => void): string;
    /**Shows a confirmation notification (with two options: Yes and No) and accepts a confirmation callback (executed if the user clicks on Yes)
    * and an optional callback that is executed if the user clicks on No, and returns the ID of the notification */
    affirm(content: string, options: options, onConfirmCallback: (evt: MouseEvent, id: string) => void, onCancelCallback?: (evt: MouseEvent, id: string) => void): string;
    /**Displays a notification with the provision for an input, which is passed to the onNextCallback when the user clicks on "Next" */
    input(title: string, options: options, onNextCallback: (evt: MouseEvent, id: string, valueEntered: string) => void, onCancelCallback?: (evt: MouseEvent, id: string) => void): string;
    /**Destroys the notification with the associated ID */
    destroy(id: string): void;
}
/**Stores the available options */
export interface options {
    /**Notification type, if custom, then customClass will hold the class name that needs to be applied. */
    type: 'success' | 'info' | 'warning' | 'danger' | 'custom' | string;
    /**Timeout in milliseconds. Default is 5000. */
    timeout?: number;
    /**Class name to be applied to the notification. `type` should be set to `custom`. */
    customClass?: string;
    /**Set the animate.css animationIn class */
    animateIn?: string;
    /**Set the animate.css animationOut class */
    animateOut?: string;
}
