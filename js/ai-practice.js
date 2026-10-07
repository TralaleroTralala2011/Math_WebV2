/* MATH WEB AI PRACTICE COMPATIBILITY BRIDGE
 * The authoritative practice AI lives in js/practise.js.
 * This file intentionally contains no second AI state machine.
 */
(() => {
    "use strict";

    function delegate() {
        if (window.MATHWEB_PRACTICE && typeof window.MATHWEB_PRACTICE.openAI === "function") {
            window.MATHWEB_PRACTICE.openAI();
            return true;
        }
        return false;
    }

    window.MATHWEB_AI_PRACTICE = {
        open: delegate,
        close() {
            if (window.MATHWEB_PRACTICE && typeof window.MATHWEB_PRACTICE.closeAI === "function") {
                window.MATHWEB_PRACTICE.closeAI();
            }
        },
        reset() {
            if (window.MATHWEB_PRACTICE && typeof window.MATHWEB_PRACTICE.closeAI === "function") {
                window.MATHWEB_PRACTICE.closeAI();
            }
        }
    };
})();
