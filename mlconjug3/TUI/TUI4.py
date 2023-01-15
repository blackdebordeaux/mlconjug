import textual
from .mlconjug import Conjugator
import json
import logging

import requests
from bs4 import BeautifulSoup

def get_verb_examples_in_context(verb):
    """
    Retrieves examples of the provided verb used in context from an external website.
    :param verb: string. The verb to retrieve examples for.
    :return: list of strings. A list of examples of the verb used in context.
    """
    url = f"https://context.reverso.net/translation/{verb}-examples"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    examples = soup.find_all("a", class_="example-sentence")
    return [example.get_text() for example in examples]


class TUI:
    def init(self):
        self.app = textual.Application(title="Verb Conjugator")
        self.left_section = self.app.add(textual.Container(flex=1))
        self.right_section = self.app.add(textual.Container(flex=1))
        self.prompt = self.left_section.add(textual.Prompt(placeholder="Enter a verb"))
        self.conjugation_tables = self.left_section.add(textual.Container(flex=1))
        self.verb_history = self.right_section.add(textual.List(flex=1))
        self.sample_verbs = self.right_section.add(textual.List(flex=1))
        self.export_button = self.right_section.add(textual.Button("Export"))
        self.language_selector = self.right_section.add(textual.Select(options=["fr", "en", "es", "it", "pt", "ro"]))
        self.subject_selector = self.right_section.add(textual.Select(options=["abbrev", "pronoun"]))
        self.help_section = self.right_section.add(textual.Container(flex=1))

        self.conjugator = Conjugator()
        self.prompt.on_submit(self.handle_submit)
        self.export_button.on_click(self.handle_export)
        self.verb_history.on_select(self.handle_history_select)
        self.language_selector.on_select(self.handle_language_select)
        self.subject_selector.on_select(self.handle_subject_select)
        self.help_section.add(textual.Text("Enter a verb in the prompt to conjugate it. Use the export button to save the conjugations. Use the language selector to choose the language for conjugation. Use the subject selector to choose between abbrev or pronoun for conjugations"))
        
    def handle_submit(self, verb):
        self.conjugator.set_language(self.language_selector.get_value())
        conjugation_result = self.conjugator.conjugate(verb, self.subject_selector.get_value())
        if conjugation_result:
            self.verb_history.add_item(verb)
            self.conjugation_tables.clear()
            for tense, conjugations in conjugation_result.items():
                tense_container = self.conjugation_tables.add(textual.Container())
                tense_container.add(textual.Label(tense))
                conjugation_table = tense_container.add(textual.Table(headers=["Subject", "Conjugation"]))
                for subject, conjugation in conjugations.items():
                    conjugation_table.add_row([subject, conjugation])
                examples = get_verb_examples_in_context(verb)
                if examples:
                    self.sample_verbs.clear()
                    for example in examples:
                        self.sample_verbs.add_item(example)
                else:
                    self.conjugation_tables.clear()
                    self.conjugation_tables.add(textual.Text("The verb is not in the dataset. The conjugation was not possible."))

    def handle_history_select(self, verb):
        """
        Handles the verb history list select event.
        Displays the conjugations for the selected verb.
        """
        self.prompt.set_text(verb)
        conjugation_result = self.conjugator.conjugate(verb, self.subject_selector.get_value())
        if conjugation_result:
            self.conjugation_tables.clear()
            for tense, conjugations in conjugation_result.items():
                tense_container = self.conjugation_tables.add(textual.Container())
                tense_container.add(textual.Label(tense))
                conjugation_table = tense_container.add(textual.Table(headers=["Subject", "Conjugation"]))
                for subject, conjugation in conjugations.items():
                    conjugation_table.add_row([subject, conjugation])
        else:
            self.conjugation_tables.clear()
            self.conjugation_tables.add(textual.Text("The verb is not in the dataset. The conjugation was not possible."))
        
    def handle_export(self):
        conjugations = {}
        for item in self.verb_history.get_items():
            conjugation_result = self.conjugator.conjugate(item, self.subject_selector.get_value())
            conjugations[item] = conjugation_result
        filename = self.prompt.get_value() + '.json'
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(conjugations, file, ensure_ascii=False, indent=4)
        self.app.alert("Conjugations exported to " + filename)

    def handle_language_select(self, language):
        self.conjugator.set_language(language)
        self.prompt.set_value('')
        self.conjugation_tables.clear()
        self.sample_verbs.clear()

    def handle_subject_select(self, subject):
        self.handle_submit(self.prompt.get_value())
        self.app.focus(self.subject_selector)
    
    def handle_similar_verb_select(self, verb):
        self.prompt.set_value(verb)
        self.handle_submit(verb)
        self.app.focus(self.prompt)
        
    def handle_export(self):
        export_format = textual.dialog.ask("What format do you want to export?", ["JSON", "CSV"])
        if export_format:
            export_path = textual.dialog.ask("Where do you want to save the file?", "file")
        if export_path:
        with open(export_path, 'w', encoding='utf-8') as file:
            json.dump(self.conjugation_tables, file, ensure_ascii=False, indent=4)
            textual.alert("The conjugations have been succesfully saved to {0}.".format(export_path))
            self.app.focus(self.export_button)
            
    def display_conjugations_in_table(self, conjugations):
        self.conjugation_tables.clear()
        headers = ["Person", "Singular", "Plural"]
        rows = []
        for person, conjugation in conjugations.items():
            rows.append([person, conjugation["singular"], conjugation["plural"]])
        table = textual.Table(headers=headers, rows=rows)
        self.conjugation_tables.add(table)
    
    def change_verb_tense(self):
        self.tense_selector = self.right_section.add(textual.Select(options=["present", "past", "future", "subjunctive", "conditional"]))
        self.tense_selector.on_select(self.handle_tense_change)

    def handle_tense_change(self, selection):
        self.tense = selection
        self.handle_submit(self.verb_input.value)
    
    def compare_multiple_conjugations(self):
        self.multiple_verb_input = self.left_section.add(textual.Prompt(placeholder="Enter multiple verbs separated by commas"))
        self.multiple_verb_input.on_submit(self.handle_multiple_submit)

    def handle_multiple_submit(self, input_text):
        verbs = input_text.split(',')
        results = {}
            for verb in verbs:
            result = self.conjugator.conjugate(verb.strip(), self.subject)
            results[verb.strip()] = result.conjug_info
        self.conjugation_tables.clear()
        for verb, conjugations in results.items():
            verb_table = self.conjugation_tables.add(textual.Table(flex=1))
            verb_table.add_column("Tense/Person", flex=1)
            verb_table.add_column(verb, flex=1)
            for tense, conjugation in conjugations.items():
                verb_table.add_row(tense, conjugation)
        self.verb_history.append(input_text)
    
    

    
        
    




    
