function GrammarianXBlock(runtime, element, initialState) {
    "use strict";

    const $element = $(element);
    element = $element[0]; // <- Works around a Studio bug in Dogwood: https://github.com/edx/edx-platform/pull/11433
    const $textBox = $element.find('.grammarian-text');
    const $parts = $textBox.find(".grammarian-part");

    var state = initialState;
    init();

    /**
     * Initialize the client-side code of this Grammarian XBlock
     */
    function init() {
        console.log("Initializing GrammarianXBlock");
        applyState();

        // set up event handlers:
        $element.on("click", ".selection-required .grammarian-part", handlePartClicked);
    };

    /**
     * Update the DOM to reflect 'state'.
     */
    function applyState() {
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
            state = responseData;
            applyState();
        });
    }
}
