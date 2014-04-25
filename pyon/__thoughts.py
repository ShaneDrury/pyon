__author__ = 'srd1g10'
"""
Chromopy - A lattice QCD fitting library.

Something like:
corr = Correlator(data, **kwargs)  # or maybe call it Hadron to distinguish it from one correlator

@corr.fit  # i.e. Hadron is an ordered list of correlators with metadata
def fit_func(data, fit_range, **kwargs):
    ...
corr.fit(fit_range=(1,32))  # ?

The point of this is that we are passing fit_func through to fit the correlator.
This means that fit_func is just some function of the data - completely general, can use sim/individual fits.
corr.fit() doesn't make any assumptions about the data, just runs fit_func.
Why not just use functions? Hadron is a collection of data and some methods attached to it. Also useful to keep metadata
with it e.g. the parameters of the hadron.

Data should probably still be kept as lists in pickle format because implementation might change - can't unpickle them
and also other modules can't read them unless they have whatever class they're in. i.e. don't pickle a Hadron object
Can keep data as one bigger pickle file for convenience, but need extra stuff like the config numbers/masses?
Maybe have a very simple class that does this? Can have a method for Hadron that outputs/loads to json. This is what
would be saved/loaded as pickle(? - maybe not - easier to read if not pickled) and is readable by anything.

class Hadron(object):
    def dumps(formatting_options):  # dump to string. all data necessary to recreate Hadron
        pass
    def dump(formatting):  # dump to file
        pass
    def loads(string):  # load from string
        pass
    def load(string):  # load from file
        pass


Thoughts about http://me.veekun.com/blog/2013/03/03/the-controller-pattern-is-awful-and-other-oo-heresy/
The point is that methods are often not related to the thing that they act with. e.g. the CleanupJob has one method
called 'run'. That run method is actually more natural to be a method of Job, but in order to have customisability
we have to support some way of changing it. Inheritance on classes would change it in the class, but we can also
change it on an instance per instance (object) level. So the way to do this is with decorators in the example given.
We prefer to do it on an object level because inheritance is a messy way to customise certain bits of classes. By
using objects we can use many other tools to say what the functionality of each object is. So run is actually part of
the state of Job. We instantiate an object of type Job and customise the state of it such that its run method is the
cleanup function.

For pyon, it is ok to have classes which are collections of data and relevant functions e.g. Hadron and possibly
Correlator. It's probably not good to have many different inheritors of Hadron e.g. meson/baryon etc since there are
so many variants of these. It's better to have a fit method which we specify at the object level since there are
so many tiny variants of customisation.

Another part which could benefit from this approach is file handling/parsing. Since each file format may share
a lot of similarities but may vary slightly it's probably best to define the parse function at the object level instead
of overriding it in each class, creating many very slightly different Parsers

But is Hadron really the object we should be concerned with? Hadron is acted on by the main body of the script, which
call its various methods. In other words the state of Hadron is its methods and something else is always calling it.
It would be possible to make another class or logical part of the program (main?) which calls the various methods which
we are doing like loading data, fitting, plotting etc. This would take the form of a list of commands that are
executed in sequence i.e. it would be a wrapper for standard python code. This probably hints at the fact that fitting
and plotting etc should be more independent of Hadron. One could pass in a Hadron to the fitting function instead of
having fit as a method of Hadron. This would mean one wouldn't have to use the decorators either. We would have better
separation of concerns i.e. to look at the fitting code you wouldn't have to look at Hadron.
The central object is the list of commands but that is best represented as a list of python commands. So the behaviour
of this 'object' is to run these commands. The state is whatever order they're in and what commands are there. I don't
think it makes sense to represent this as a python object.

Of course, in every program the central object is the list of commands so we have to assume that is represented by the
code and go to the next central object. Actually it's best to think of the next N central objects, since there should
be no other master object apart from the list of commands that controls things (at least in this simple case).
Or should there? In Flask for example, the central object is clearly the app and the list of commands of the python
program simply sets the state of the app. Then calling app.run() sets things in motion. It is like we delegate the
role of the central object to the app object. In my case I am not delegating things to a central app since it is
both useful to keep the explicitness of the code and to keep the customisability.

As to taking 'fit' out of Hadron. It's nice to have a fit function associated with a particular Hadron e.g. meson.
If we were to take it out and make a fit method, we would have to pass in the fit_function. This could be part of
Hadron instead. So, we would set the fit_function of each Hadron to customise it, but wouldn't set the fit method.
This is actually a good idea since we can have a simultaneous fit or an individual fit for the same Hadron type.
So the fit function is what we customise. This could be done with a class Fitter and we customise the method fit?
That might leave us with a class with effectively one method which should really be a function. Can use a library of
functions which we just call.

Could Correlator be better represented as a dict? The Correlator class is just an init and some way of adding
Correlators. The only reason for adding correlators is to take the average, and we can just define a function to do
this. Correlator could look like:
corr = {'data': [[...], [...], ...], 'config_numbers': [1, 3, 5, ...], ...}
or:
corr = {'data': [{'data': [...], 'config_number': 1}, {...}, ...], 'masses': (0.01, 0.01)}  # probably better
Correlator doesn't have any methods and it certainly doesn't have behaviour, just state.

Hadron is like a wrapper around some data. Is it better represented as a dict? We would have helper functions to
construct Mesons which would access hadron['fit_func'] instead of hadron.fit_func.
I think in this case, it may be easier to have Hadron as a class. A class is a set of state and behaviour.
The state is the data. The fit_func is also the state of the Hadron since it is a property of the Hadron.
Thus Hadron doesn't have any methods either! It is, however useful to keep all of this data in one object.
A possible method for Hadron is to fold/sort the data in which case it is reasonable to keep it as a class.

===

Other thoughts. Could structure it more like an app. When we use Pyon as a library, it may be useful to call its
individual functions and structure a module as a single script. What might be more useful is to parse some xml and
have an 'app' object which runs through the elements and runs them in order. It would abstract away all the nuts
and bolts of fitting/plotting etc. This could exist entirely on top of the other stuff so that if the user wishes, they
can have more granularity.

Another idea is from Django. Django splits the elements of a site up into various files. So the function of an entire
site is split up into different modules. This is designed so that portions of functionality can be maintained
independently of each other. It's the idea of an 'app' that exists across multiple files and not explicitly having
a 'main' function. In django, you do 'python manage.py runserver' which pulls together all the various modules
and makes them interact but there is no central function. This keeps very loose coupling.
So for Pyon, an 'app' would be a particular set of functionalities. Each functionality would use elements of the library
but there wouldn't be a main script which just runs through each command. I think this would be useful because lattice
QCD projects vary wildly and you end up doing the same thing multiple times. Like taking the mass-squared difference
of mesons. However, the mass-squared difference of mesons isn't a fundamental enough concept to have in the Pyon library
itself, so we could have it in an app that uses the Pyon library functions. Each app may be installed alongside other
apps to bring in loosely coupled functionality. The Pyon library would be common use cases (batteries included) and
a way to bring apps together ala Django.
"""

