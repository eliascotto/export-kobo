# export-kobo
A Python tool to export annotations and highlights from a Kobo SQLite file. This is a maintained version of [export-kobo](https://github.com/pettarin/export-kobo) by Alberto Pettarin.

Works with Python 3 only.

**Tested with latest Kobo Clara**

## Usage

```bash
$ # print all annotations and highlights to stdout
$ python3 export-kobo.py KoboReader.sqlite

$ # print the help
$ python3 export-kobo.py --help

$ # export to file instead of stdout
$ python3 export-kobo.py KoboReader.sqlite --output /path/to/out.txt

$ # export in CSV format
$ python3 export-kobo.py KoboReader.sqlite --csv

$ # export in Kindle My Clippings format
$ python3 export-kobo.py KoboReader.sqlite --kindle

$ # export in Markdown list format
$ python3 export-kobo.py KoboReader.sqlite --markdown

$ # export annotations only
$ python3 export-kobo.py KoboReader.sqlite --annotations-only

$ # export highlights only
$ python3 export-kobo.py KoboReader.sqlite --highlights-only

$ # export as CSV to file annotations only
$ python3 export-kobo.py KoboReader.sqlite --csv  --annotations-only --output /path/to/out.txt

$ # print the list of books with annotations or highlights to stdout
$ python3 export-kobo.py KoboReader.sqlite --list

$ # export annotations and highlights for the book "Alice in Wonderland"
$ python3 export-kobo.py KoboReader.sqlite --book "Alice in Wonderland"

$ # as above, assuming "Alice in Wonderland" has ID "12" in the list printed by --list
$ python3 export-kobo.py KoboReader.sqlite --bookid 12
```

Example output
```
Type:           highlight
Title:          Alice in Wonderland
Author:         Lewis Carroll
Chapter:        CHAPTER II. The Pool of Tears
Date created:   Tuesday, 27 October 2020 07:04:48
Annotation:
### ### ###
Poor Alice!
### ### ###

Reference text:
=== === ===
“Curiouser and curiouser!” cried Alice (she was so much surprised, that for the moment she quite forgot how to speak good English);
=== === ===

...
```

## Installation


1. Clone this repository:
    ```bash
    $ git clone https://github.com/elias94/export-kobo
    ```
   or manually download the ZIP file from the [Releases tab](https://github.com/elias94/export-kobo/releases/) and unzip it somewhere;

3. Enter the directory where ``export-kobo.py`` is:
    ```bash
    $ cd export-kobo
    ```

4. Copy in the same directory the ``KoboReader.sqlite`` file
   from the ``.kobo/`` hidden directory of the USB drive
   that appears when you plug your Kobo device to the USB port of your PC.
   You might need to enable the ``View hidden files`` option
   in your file manager to see the hidden directory;
   Examples command to copy the sql file from the Kobo Reader on MacOS and Linux. 
   ```bash
   $ cp /Volumes/KOBOeReader/.kobo/KoboReader.sqlite ./
   ```

5. Now you can run the script as explained above, for example:
    ```bash
    $ python3 export-kobo.py KoboReader.sqlite
    ```

NOTE (2018-02-28): Frederic Da Vitoria confirms that the export script
also works if you have the Kobo application for Windows PC.
In this case the database file is called ``Kobo.sqlite``
and is located in the directory
``C:\Users\[your user name]\AppData\Local\Kobo\Kobo Desktop Edition\``.


## Troubleshooting

### I ran the script, but I obtained too much data

If you want to output annotations or highlights for a single book,
you can use the ``--list`` option to list all books with annotations or highlights,
and then use ``--book`` or ``--bookid`` to export only those you are interested in:

``` bash
$ python3 export-kobo.py KoboReader.sqlite --list
ID  Title
1   Alice in Wonderland
2   Moby Dick
3   Sonnets
...

$ python3 export-kobo.py KoboReader.sqlite --book "Alice in Wonderland"
...
$ python3 export-kobo.py KoboReader.sqlite --bookid 1
...
```

You can also exporting to a file redurecting the output of the script:
``` bash
$ python3 export-kobo.py KoboReader.sqlite --bookid 1 > Alice\ in\ Wonderland.txt
```

Alternatively, you can export to a CSV file with ``--csv --output FILE``
and then open the resulting output file with a spreadsheet application,
disregarding the annotations/highlights you are not interested in:

```bash
$ python3 export-kobo.py KoboReader.sqlite --csv --output notes.csv
$ libreoffice notes.csv
```

### I filtered my notes by book title with ``--book``, but I got no results

Check that you wrote the book title exactly as printed by ``--list``
(e.g., copy-and-paste it), or use ``--bookid`` instead.


## Notes

1. Around May 2016 Kobo changed the schema
   of their ``KoboReader.sqlite`` database with a firmware update.
   The ``export-kobo.py`` script in the main directory of this repository
   works for this **new** database schema.
   If you still have an old firmware on your Kobo,
   and hence the old database schema,
   you might want to use one of the scripts in the ``old/`` directory.
   Note, however, that those scripts are very old, possibly buggy,
   and they are no longer supported
   ([old Web page](http://www.albertopettarin.it/exportnotes.html)).

2. Since I no longer use a Kobo eReader,
   this project is maintained in "legacy mode".
   Changes to the schema of the ``KoboReader.sqlite`` database
   can be reflected on the code
   only thanks to users sending me their ``KoboReader.sqlite`` file,
   for me to study its schema.

3. Bear in mind that no official specifications are published by Kobo,
   hence the script works as far as
   my understanding of the database structure of ``KoboReader.sqlite`` is correct,
   and its schema remains the same.

4. Although the ``KoboReader.sqlite`` file is opened in read-only mode,
   it is advisable to make a copy of it on your PC
   and export your notes from this copy,
   instead of directly accessing the file on your Kobo eReader device.
   
## Difference from Original Version

The original version of this script is from [Alberto Pettarin](https://github.com/pettarin). The [original repository](https://github.com/pettarin/export-kobo) is currenlty archivied and no longer maintained, and in the comments the author says that he hasn't anymore a Kobo reader.

* Cleaned code
* Removed support for python2
* Added Chapter information to the output
* Restyled output of list and annotations
* Sort highlight/annotations by `datecreated`
* Export in Markdown format

## Acknowledgments

* Chris Krycho contributed a fix for a typo in month names.
* Pierre-Arnaud Rabier suggested adding an option to extract the annotations and highlights for a single ebook.
* Nick Kalogirou and Andrea Moro provided me with theirs KoboReader.sqlite file with the new schema.
* Curiositry suggested adding an option to extract in Kindle My Clippings format.
* Frederic Da Vitoria confirmed that the export script works for the Kobo app for Desktop PC.
* Matthieu Nantern contributed the ``raw`` export mode.


## License

**export-kobo** is released under the MIT License.


---

Elia Scotto | [Website](https://www.eliascotto.com)
