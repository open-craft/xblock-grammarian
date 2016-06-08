# -*- coding: utf-8 -*-
"""
Grammarian: An XBlock that displays a sentence and asks the learner to click on the part of
the sentence that is incorrect. It is intended to reinforce lessons in grammar, syntax, or
programming.
"""

from __future__ import unicode_literals

import jinja2
from xblock import fields
from xblock.core import XBlock
from xblock.exceptions import JsonHandlerError
from xblock.fields import Scope
from xblock.fragment import Fragment
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .utils import split_sentence_into_parts


template_engine = jinja2.Environment(loader=jinja2.PackageLoader('grammarian'))


def _(text):
    """ No-op function used to mark strings that will need to be translated. """
    return text


class GrammarianXBlock(XBlock, StudioEditableXBlockMixin):
    """
    Implements the Grammarian XBlock
    """

    ############################################################################################
    # Fields
    ############################################################################################

    # Configuration:
    display_name = fields.String(
        display_name=_("Title"),
        help=_("The title of this problem. Displayed to learners as a tooltip in the navigation bar."),
        scope=Scope.settings,
        default=_("Identify the error"),
    )

    instructions = fields.String(
        display_name=_("Instructions"),
        help=_("The description of the problem or instructions shown to the learner."),
        scope=Scope.settings,
        default=_(
            "Is there an error in the following sentence? "
            "Click on the part of the sentence that is incorrect."
        ),
    )

    text = fields.String(
        display_name=_("Text"),
        help=_(
            "The text shown to the learner. "
            "The learner will choose the part of this text that they believe contains the error. "
            "Surround the error with square brackets (e.g. \"[It's] surface was cracked.\" "
        ),
        scope=Scope.settings,
        default=_("What [affect] has it had on your life?"),
    )

    # User state:
    part_selected = fields.Integer(
        # The part of the sentence the user selected.
        # The sentence "It's surface was cracked!" would be split into these parts:
        # ["It's", " ", "surface", " ", "was", " ", "cracked", "!"]
        # If the user clicked on "surface", the value of this field would be 2.
        scope=Scope.user_state,
        default=None,
    )

    ############################################################################################
    # Other properties of this XBlock:
    ############################################################################################

    has_score = True
    editable_fields = ('display_name', 'instructions', 'text')

    ############################################################################################
    # Helpful properties and methods
    ############################################################################################

    @property
    def text_parts(self):
        """
        Get the parts of the text.

        If self.text is "What [affect] has it had on your life?", then this will return:
            ['What', ' ', 'affect', ' ', 'has', ' ', 'it', ' ', 'had', ' ', 'on', ..., '?']
        """
        parts, unused_wrong_index = split_sentence_into_parts(self.text)
        return parts

    @property
    def wrong_part_index(self):
        """
        Get the index of the part that the instructor has indicated is wrong.

        May return None if the instructor has not marked the wrong part correctly.
        """
        unused_parts, wrong_index = split_sentence_into_parts(self.text)
        return wrong_index

    @property
    def student_has_answered(self):
        """ Has the student made a choice yet? """
        return self.part_selected is not None

    def get_current_state(self):
        """
        Get the current state (the details that are user-specific and which can change)
        """
        state = {
            "selected_part_index": self.part_selected,
        }
        # Only include the correct answer if the student has already guessed:
        if self.student_has_answered:
            state["wrong_part_index"] = self.wrong_part_index
        return state

    ############################################################################################
    # Views
    ############################################################################################

    def student_view(self, context):
        """
        The main view of this XBlock.
        """
        template = template_engine.get_template('student_view.html')
        html = template.render({
            "title": self.display_name,
            "instructions": self.instructions,
            "text_parts": self.text_parts,
            "selected_part_index": self.part_selected,
            "wrong_part_index": self.wrong_part_index if self.student_has_answered else None,
        })
        fragment = Fragment(html)
        fragment.add_css_url(self.runtime.local_resource_url(self, 'public/style.css'))
        fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/client.js'))

        fragment.initialize_js('GrammarianXBlock', self.get_current_state())

        return fragment

    ############################################################################################
    # Client-side AJAX callback handlers
    ############################################################################################

    @XBlock.json_handler
    def select_part(self, data, suffix=''):
        """
        Get the state of this XBlock - i.e. all the user-specific data
        """
        if self.student_has_answered:
            raise JsonHandlerError(400, "This student already answered.")
        part_index = data.get("part_index")
        if part_index not in range(0, len(self.text_parts)):
            raise JsonHandlerError(400, "Invalid part_index.")

        # Save the student's selection:
        self.part_selected = part_index

        return self.get_current_state()

    ############################################################################################
    # Misc
    ############################################################################################

    @staticmethod
    def workbench_scenarios():
        """
        An XML scenario for display in the XBlock SDK workbench.
        """
        return [
            ("Grammarian default scenario", "<grammarian/>"),
        ]
