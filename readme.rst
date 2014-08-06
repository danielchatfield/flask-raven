Flask_raven: University of Cambridge authentication for flask
=============================================================


This is a very simple package that satisfies my needs, there is a more complex
package here: https://github.com/danielrichman/python-raven that I couldn't use
because of it depends on C modules which are blocked on App Engine.


Usage
-----

.. code-block:: python

    from flask_raven import raven_auth

    @app.route('/protected')
    @raven_auth()
    def protected():
        pass
