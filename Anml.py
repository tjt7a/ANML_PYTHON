'''
    This serves as the ANML class file in Python with support for
    counters
    Author: Tom Tracy II (tjt7a@virginia.edu)
    
    ** WARNING: Macros and non-STEs are still under construction **
    ** WARNING: Because of the way __init__ works, this code will only work with Python3.0
'''
from enum import Enum


class AnmlDefs(Enum):
    """ Enums for valid start states"""
    ALL_INPUT = 1
    NO_START = 2
    START_OF_DATA = 3


class Element(object):
    """ Parent class for ANML elements including:
        STE, counter
    """

    def __init__(self, *args, **kwargs):

        # A list of elements that this element is connected to
        self.neighbors_ = []

        # The unique id of this element
        self.id_ = str(kwargs['anmlId'])

        # The type of this element
        self.type_ = self.__class__.__name__

        # Verifying that the id is a string
        assert type(self.id_) == str, "{} ID {} is not valid".format(
            self.type_, self.id_)

    def add_edge(self, element):
        """This function connects self to another element"""
        
        assert isinstance(
            element, Element), "{} is not a valid Element type".format(element)

        # Adding the element to the list of neighbors
        self.neighbors_.append(element)

    def add_edges(self, elements):
        """This function connects self to several elements"""

        # Add each element as a new neighbor
        for element in elements:
            self.add_edge(element)


class Counter(Element):
    """A class that represents a counter element in an automata network"""

    def __init__(self, *args, **kwargs):
        
        # Call the parent class's init method first, then add element-specific code
        super().__init__(*args, **kwargs)

        # Set the count target for the counter
        self.at_target_ = str(args[0])

    def __str__(self):
        """A function that prints out the ANML-formatted counter representation"""
        
        string = "\t\t<counter " + \
            "at-target=\"" + self.at_target + "\" " + \
            "id=\"" + self.id_ + "\">\n"

        # Iterate through each neighbor and add edge
        for neighbor in self.neighbors_:
            string += "\t\t\t<activate-on-target " + \
                "element=\"" + neighbor.id_ + "\"/>\n"

        string += "\t\t</counter>\n"
        return string


class Ste(Element):
    """ A class that represents an automaton state"""

    # anmlId, character_class, defs, match=False, reportCode=None):
    def __init__(self, *args, **kwargs):

        # Call the parent class's init method first, then add element-specific code
        super().__init__(*args, **kwargs)

        # Load character class and defs
        self.character_class_ = args[0]
        self.defs_ = args[1]

        if 'reportCode' in kwargs:
            self.reportCode_ = str(kwargs['reportCode'])
        else:
            self.reportCode_ = None

        if 'match' in kwargs:
            self.matching_ = kwargs['match']
        else:
            self.matching_ = False

        if self.defs_ == AnmlDefs.ALL_INPUT:
            self.starting_ = True
            self.start_type_ = 'all-input'
        elif self.defs_ == AnmlDefs.START_OF_DATA:
            self.starting_ = True
            self.start_type_ = 'start-of-data'
        else:
            self.starting_ = False
            self.start_type = 'no-start'

    def __str__(self):

        string = "\t\t<state-transition-element id=\"" + self.id_ + "\" " + \
            "symbol-set=\"" + ''.join(self.character_class_) + "\" "
        if self.starting_:
            string += "start=\"" + self.start_type_ + "\">\n"
        else:
            string += ">\n"
        if self.matching_:
            string += "\t\t\t<report-on-match reportcode=\"" +\
                self.reportCode_ + "\"/>\n"
        for neighbor in self.neighbors_:
            string += "\t\t\t<activate-on-match element=\"" + \
                neighbor.id_ + "\"/>\n"
        string += "\t\t</state-transition-element>\n"
        return string


class Anml(object):
    """A class that represents an automaton graph."""

    def __init__(self, aId="an1"):
        self.elements_ = []
        self.id_ = aId

    def __str__(self):
        """String representation of the ANML network generates the ANML file"""

        string = "<anml version=\"1.0\"  xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n"
        string += "\t<automata-network id=\"" + self.id_ + "\">\n"
        for element in self.elements_:
            string += str(element)
        string += '\t</automata-network>\n'
        string += '</anml>\n'
        return string

    def AddSTE(self, *args, **kargs):
        """Add one state to the network"""

        ste = Ste(*args, **kargs)

        self.elements_.append(ste)
        return ste
    
    def AddCounter(self, *args, **kargs):
        """Add one counter to the network"""

        counter = Counter(*args, **kargs)

        self.elements_.append(counter)
        return counter

    def AddAnmlEdge(self, element1, element2, *other):
        """Add an edge between element1 and element2"""

        element1.add_edge(element2)

    def AddAnmlEdges(self, element1, elements, *other):
        """Add an edge between element1 and all elements in elements"""

        element1.add_edges(elements)

    def ExportAnml(self, filename):
        """Write out the automaton network to a file"""

        with open(filename, 'w') as f:
            f.write(str(self))
        
        return 0
    
    def CreateMacroDef(self, **kwargs):
        """Function for creating a macro definition"""
        
        macro = Macro(**kwargs)
        
        return macro

class Macro(Anml):
    """ A class that represents a Macro definition inherits from Anml"""
    
    class Parameter(object):
        """ Class definition for Macro Parameters"""
        
        def __init__(self, name, default_value):
            self.name_ = None
            self.default_value_ = None

    def __init__(self, *args, **kwargs):

        self.id_ = str(kwargs['anmlId'])
        #self.name_ = str(kwargs['name'])
        self.parameters_ = []
    
    def AddMacroParam(self, *args, **kwargs):
        """Add a parameter to the macro definition"""
        
        parameter = Parameter(kwargs['paramName'], kwargs['elementRefs'])
        
        self.parameters_.append(parameter)
        
    
    def __str__(self):
        """Override ANML's __str__ method for Macros"""

        string = "<macro-definition id=\"" + self.id_ + "\" + name=\"" + self.name_ + "\">\n"
        string += "\t<header>\n"
        string += "\t\t<interface-declarations>\n"
        # for interface_declaration in interface_declarations: **For now not implemented**
        string += "\t\t</interface-declarations\n"

        string += "\t\t<parameter-declarations>\n"
        for parameter in self.parameters_:
            string += "\t\t\t<parameter parameter-name=\"" + parameter.name_ + \
                "\""
            if parameter.default_value_:
                string += " default-value=\"" + parameter.default_value + "\"/>\n"
        string += "\t\t</parameter-declarations>\n"
        string += "\t</header>\n"

        string += "\t<body>\n"
        string += "\t\t<port-definitions>\n"
        # for port_definition in port_definitions: **For now not implemented**
        string += "\t\t</port-definitions>\n"

        for element in self.elements_:
            string += '\t\t\t' + str(element)

        string += "\t</body>"
        string += '</macro-definition>\n'
        return string


if __name__ == "__main__":
    """ Test the class definitions"""

    anml = Anml()

    stes = []

    report_symbol = r"\x%02X" % 255

    for i in range(10):
        if i == 0:
            start_ste = anml.AddSTE(report_symbol, AnmlDefs.ALL_INPUT,
                                    anmlId=i, match=False)
            stes.append(start_ste)
        else:
            character_class = r"\x%02X" % i
            ste = anml.AddSTE(character_class, AnmlDefs.NO_START,
                              anmlId=i, match=False)
            anml.AddAnmlEdge(stes[-1], ste, 0)
            stes.append(ste)

    ste = anml.AddSTE(report_symbol, AnmlDefs.NO_START,
                      anmlId=10, reportCode=10)
    anml.AddAnmlEdge(stes[-1], ste, 0)
    anml.ExportAnml("test_anml.anml")
