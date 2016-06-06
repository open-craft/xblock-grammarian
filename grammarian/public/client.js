function GrammarianXBlock(runtime, element, initialState) {
    "use strict";

    const $element = $(element);
    element = $element[0]; // <- Works around a Studio bug in Dogwood: https://github.com/edx/edx-platform/pull/11433
    const usageId = $element.data("usage-id") || $element.data("usage"); // usage-id in LMS/Studio, usage in workbench
    // Create a global variable to save the state so sequential doesn't wipe out local changes:
    window.grammarianState = window.grammarianState || {};
    // initialState may have been cached by the parent sequential block; check if newer state is available:
    initialState = window.grammarianState[usageId] || initialState;
    var state;

    const $textBox = $element.find('.grammarian-text');
    const $parts = $textBox.find(".grammarian-part");

    init();

    /**
     * Initialize the client-side code of this Grammarian XBlock
     */
    function init() {
        console.log("Initializing GrammarianXBlock");
        applyState(initialState);

        // set up event handlers:
        $element.on("click", ".selection-required .grammarian-part", handlePartClicked);
    };

    /**
     * Update the DOM to reflect 'state'.
     */
    function applyState(newState) {
        window.grammarianState[usageId] = state = newState;
        const selectionAlreadyMade = (state.selected_part_index !== null);
        $textBox.toggleClass("selection-made", selectionAlreadyMade);
        $textBox.toggleClass("selection-required", !selectionAlreadyMade);

        // Mark one part as selected, if applicable
        $parts.removeClass("selected correct incorrect");
        if (selectionAlreadyMade) {
            const $part = $parts.eq(state.selected_part_index);
            $part.addClass("selected");
            if (state.selected_part_index === state.wrong_part_index) {
                $part.addClass("correct");
            } else {
                $part.addClass("incorrect");
            }
        }
        // If the user guessed incorrectly, show them what the real answer was:
        if (state.wrong_part_index !== undefined && state.selected_part_index !== state.wrong_part_index) {
            $parts.eq(state.wrong_part_index).addClass("correct");
        }
    };


    /**
     * The user has selected the part that they believe contains an error.
     */
    function handlePartClicked(event) {
        event.preventDefault();
        if (state.selected_part_index !== null) {
            throw "Error: A selection has already been made. Cannot make a second selection.";
        }

        const url = runtime.handlerUrl(element, 'select_part');
        const partIndex = $(event.target).index();
        const data = {part_index: partIndex};

        $.post(url, JSON.stringify(data), 'json').done(function(responseData) {
            // Upon successful submission of this selection, the updated state is returned:
            applyState(responseData);
        });
    }
}
