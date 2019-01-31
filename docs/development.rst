Development
===========

This assumes :code:`git` and :code:`Python` 3.3 or above are already installed on your system.

1. Fork the `repository source code <https://github.com/EBU/ai-benchmarking-stt.git>`_ from github to your own account.

2. Clone the repository from github to your local development environment (replace :code:`[YOURUSERNAME]` with your
   github username.

   .. code-block:: bash

      git clone https://github.com/[YOURUSERNAME]/ai-benchmarking-stt.git
      cd ai-benchmarking-stt

3. Install the package using :code:`pip`, this will also install all requirements. This does an "editable" install, i.e.
   it creates a symbolic link to the source code.

   .. code-block:: bash

      pip install -e .

4. You now have a local development environment where you can commit and push to your own forked repository.
