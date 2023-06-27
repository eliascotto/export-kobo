import argparse
import datetime
import csv
import io
import os
import sqlite3
import sys
from flask import Flask, g, render_template


DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

app = Flask(__name__)
book_manager = None

@app.before_request
def before_request():
    g.book_manager = book_manager

@app.route('/')
def index():
    """
    Index page displays only the list of books.
    """
    books = [x[1] for x in g.book_manager.get_books()]
    return render_template('index.html', books=books)

@app.route('/book/<int:book_id>')
def book_details(book_id):
    """
    When user click on a book, show all the information displayed.
    """
    books = [x[1] for x in g.book_manager.get_books()]
    (book, items) = g.book_manager.get_book_with_items_by_index(book_id)
    if book and items:
        return render_template('index.html', books=books, book=book, book_items=items)
    else:
        return "Book not found."


class CommandLineTool(object):
    """
    A class providing a generic command line tool,
    with the associated functions, error reporting, etc.

    It is based on ``argparse``.
    """
    # overload in the actual subclass
    #
    AP_PROGRAM = sys.argv[0]
    AP_DESCRIPTION = "Generic Command Line Tool"
    AP_ARGUMENTS = [
        # required args
        # {"name": "foo", "nargs": 1, "type": str, "default": "baz", "help": "Foo help"},
        #
        # optional args
        # {"name": "--bar", "nargs": "?", "type": str,, "default": "foofoofoo", "help": "Bar help"},
        # {"name": "--quiet", "action": "store_true", "help": "Do not output to stdout"},
    ]

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog=self.AP_PROGRAM,
            description=self.AP_DESCRIPTION
        )
        self.vargs = None
        for arg in self.AP_ARGUMENTS:
            if "action" in arg:
                self.parser.add_argument(
                    arg["name"],
                    action=arg["action"],
                    help=arg["help"]
                )
            else:
                self.parser.add_argument(
                    arg["name"],
                    nargs=arg["nargs"],
                    type=arg["type"],
                    default=arg["default"],
                    help=arg["help"]
                )

    def run(self):
        """
        Run the command line tool.
        """
        self.vargs = vars(self.parser.parse_args())
        self.actual_command()
        sys.exit(0)

    def actual_command(self):
        """
        The actual command to be run.

        This function is meant to be overridden in an actual subclass.
        """
        self.print_stdout("This script does nothing. Invoke another .py")

    def error(self, message):
        """
        Print an error and exit with exit code 1.
        """
        self.print_stderr("ERROR: {}".format(message))
        sys.exit(1)

    def print_stdout(self, *args, **kwargs):
        """
        Print to standard out.
        """
        print(*args, **kwargs)

    def print_stderr(self, *args, **kwargs):
        """
        Print to standard error.
        """
        print(*args, file=sys.stderr, **kwargs)


class Item(object):
    """
    A class representing one of: annotation, bookmark, or highlight.

    It is basically a named tuple, with some extra functions to
    format the contents.
    """

    ANNOTATION = "annotation"
    BOOKMARK = "bookmark"
    HIGHLIGHT = "highlight"

    def __init__(self, values, book):
        self.volumeid = values[0]
        self.text = values[1].strip().rstrip() if values[1] else None
        self.annotation = values[2]
        self.extraannotationdata = values[3]
        self.datecreated = values[4] if values[4] is not None else "1970-01-01T00:00:00.000"
        self.datemodified = values[5] if values[5] is not None else "1970-01-01T00:00:00.000"
        self.booktitle = book.title
        self.chapter = values[7]
        self.author = book.author
        self.kind = self.BOOKMARK

        if (self.text is not None) and (self.text != "") and (self.annotation is not None) and (self.annotation != ""):
            self.kind = self.ANNOTATION
        elif (self.text is not None) and (self.text != ""):
            self.kind = self.HIGHLIGHT

    def csv_tuple(self):
        """
        Return a tuple representing this Item, for CSV output purposes.
        """
        return (self.kind, self.booktitle, self.author, self.chapter, self.datecreated, self.datemodified, self.annotation, self.text)

    def markdown(self):
        """
        Output markdown item contains only highlights and notes.
        """
        if self.kind == self.ANNOTATION:
            output = "- {}\n\n  *{}*\n\n".format(self.text, self.annotation)
        elif self.kind == self.HIGHLIGHT:
            output = "- {}\n\n".format(self.text)
        else:
            output = ""
        return output

    def format_date(self):
        d = "Thursday, 1 January 1970 00:00:00"
        try:
            p1, p2 = self.datecreated.split("T")
            year, month, day = [int(x) for x in p1.split("-")]
            hour, minute, second = [int(float(x)) for x in p2.split(":")]
            sday = DAYS[datetime.datetime(year=year, month=month, day=day).weekday()]
            smonth = MONTHS[month - 1]
            # e.g. "Friday, 19 December 2014 19:54:11"
            d = "{}, {} {} {} {:02d}:{:02d}:{:02d}".format(sday, day, smonth, year, hour, minute, second)
        except:
            pass
        return d

    def kindle_my_clippings(self):
        """
        Return a string representing this Item, in the Kindle "My Clippings" format.
        """
        date = self.format_date()
        output = []
        output.append("{} ({})".format(self.title, self.author))
        if self.kind == self.ANNOTATION:
            output.append("- Your Note on page {} | location {} | Added on {}".format(1, 1, date))
            output.append("")
            output.append(self.annotation)
        elif self.kind == self.HIGHLIGHT:
            output.append("- Your Highlight on page {} | location {} | Added on {}".format(1, 1, date))
            output.append("")
            output.append(self.text)
        else:
            output.append("- Your Bookmark on page {} | location {} | Added on {}".format(1, 1, date))
            output.append("")
        output.append("==========")
        return "\n".join(output)

    def __repr__(self):
        return "({})".format(self.csv_tuple())

    def __str__(self):
        output = []
        hsep = "\n=== === ===\n"
        asep = "\n### ### ###\n"
        date = self.format_date()
        if self.kind == self.ANNOTATION:
            output.append("Type:           {}".format(self.kind))
            output.append("Title:          {}".format(self.booktitle))
            output.append("Author:         {}".format(self.author))
            output.append("Chapter:        {}".format(self.chapter))
            output.append("Date created:   {}".format(date))
            output.append("Annotation:     {}{}{}".format(asep, self.annotation, asep))
            output.append("Reference text: {}{}{}".format(hsep, self.text, hsep))
        if self.kind == self.HIGHLIGHT:
            output.append("Type:           {}".format(self.kind))
            output.append("Title:          {}".format(self.booktitle))
            output.append("Author:         {}".format(self.author))
            output.append("Chapter:        {}".format(self.chapter))
            output.append("Date created:   {}".format(date))
            output.append("Reference text: {}{}{}".format(hsep, self.text, hsep))
        return "\n".join(output)


class Book(object):
    """
    A class representing a book.

    It is basically a named tuple, with some extra functions to
    format the contents.
    """

    def __init__(self, values):
        self.volumeid = values[0]
        self.booktitle = values[1]
        self.title = values[2]
        self.author = values[3]

    def __repr__(self):
        return "({}, {}, {}, {})".format(self.volumeid, self.booktitle, self.title, self.author)

    def __str__(self):
        return self.__repr__()

    def to_markdown(self):
        return "# {}\n## by {}\n---\n\n".format(self.title, self.author)


class ExportKobo(CommandLineTool):
    """
    The actual command line tool to export
    annotations, bookmarks, and highlights
    from a Kobo SQLite file.
    """

    AP_PROGRAM = "export-kobo"
    AP_DESCRIPTION = "Export annotations and highlights from a Kobo SQLite file."
    AP_ARGUMENTS = [
        {
            "name": "db",
            "nargs": None,
            "type": str,
            "default": None,
            "help": "Path of the input KoboReader.sqlite file"
        },
        {
            "name": "--ui",
            "action": "store_true",
            "help": "Start a web server to navigate the books"
        },
        {
            "name": "--output",
            "nargs": "?",
            "type": str,
            "default": None,
            "help": "Output to file instead of using the standard output"
        },
        {
            "name": "--csv",
            "action": "store_true",
            "help": "Output in CSV format instead of human-readable format"
        },
        {
            "name": "--markdown",
            "action": "store_true",
            "help": "Output in Markdown list format"
        },
        {
            "name": "--kindle",
            "action": "store_true",
            "help": "Output in Kindle 'My Clippings.txt' format instead of human-readable format"
        },
        {
            "name": "--list",
            "action": "store_true",
            "help": "List the titles of books with annotations or highlights"
        },
        {
            "name": "--book",
            "nargs": "?",
            "type": str,
            "default": None,
            "help": "Output annotations and highlights only from the book with the given title"
        },
        {
            "name": "--bookid",
            "nargs": "?",
            "type": str,
            "default": None,
            "help": "Output annotations and highlights only from the book with the given ID"
        },
        {
            "name": "--annotations-only",
            "action": "store_true",
            "help": "Outputs annotations only, excluding highlights"
        },
        {
            "name": "--highlights-only",
            "action": "store_true",
            "help": "Outputs highlights only, excluding annotations"
        },
        {
            "name": "--info",
            "action": "store_true",
            "help": "Print information about the number of annotations and highlights"
        },
        {
          "name": "--raw",
          "action": "store_true",
          "help": "Output in raw text instead of human-readable format"
        },
    ]

    # Query all books info and add Attribution with a Join using VolumeID
    QUERY_ITEMS = """
        SELECT 
         Book.VolumeID, 
         Book.Text, 
         Book.Annotation, 
         Book.ExtraAnnotationData, 
         Book.DateCreated, 
         Book.DateModified, 
         Book.BookTitle, 
         Book.Title, 
         Attr.Attribution 
        FROM (
          SELECT 
            Bookmark.VolumeID, 
            Bookmark.Text, 
            Bookmark.Annotation, 
            Bookmark.ExtraAnnotationData, 
            Bookmark.DateCreated, 
            Bookmark.DateModified, 
            content.BookTitle, 
            content.Title, 
            content.Attribution, 
            content.ContentID 
          FROM Bookmark INNER JOIN content 
          ON Bookmark.ContentID = content.ContentID 
        ) as Book 
        LEFT JOIN (
          SELECT 
            Bookmark.VolumeID, 
            content.Attribution 
          FROM Bookmark INNER JOIN content 
          ON Bookmark.VolumeID = content.ContentID 
        ) as Attr 
        ON Book.VolumeID = Attr.VolumeID 
        GROUP BY Book.DateCreated 
        ORDER BY Book.DateCreated ASC;
    """

    QUERY_BOOKS = """
        SELECT DISTINCT 
        Bookmark.VolumeID, 
        content.BookTitle, 
        content.Title, 
        content.Attribution 
        FROM Bookmark INNER JOIN content 
        ON Bookmark.VolumeID = content.ContentID 
        ORDER BY content.Title;
    """

    def __init__(self):
        super(ExportKobo, self).__init__()
        self.books = []
        self.items = []

    def actual_command(self):
        """
        The main function of the tool: parse the parameters,
        read the given SQLite file, and format/output data as requested.
        """
        if self.vargs["db"] is None:
            self.error("You must specify the path to your KoboReader.sqlite file.")

        # list of books
        dict_books, enum_books = self.extract_books()
        # annotations and highlights
        self.items = self.read_items(dict_books, enum_books)

        if self.vargs["ui"]:
            self.run_server()
        else:
            if self.vargs["list"]:
                # export list of books
                output = []
                output.append(("ID", "AUTHOR", "TITLE"))

                for (i, b) in enum_books:
                    output.append((i, b.author, b.title))

                if self.vargs["csv"]:
                    output = self.list_to_csv(output)
                else:
                    frmt = lambda v: "{}\t{:30}\t{}".format(v[0], v[1] or "None", v[2] or "None")
                    output = "\n".join([frmt(v) for v in output])
            else:
                # export annotations and/or highlights
                if self.vargs["kindle"]:
                    # kindle format
                    output = "\n".join([i.kindle_my_clippings() for i in self.items])
                elif self.vargs["csv"]:
                    # CSV format
                    output = self.list_to_csv([i.csv_tuple() for i in self.items])
                elif self.vargs["markdown"]:
                    output = self.list_to_markdown(enum_books)
                elif self.vargs["raw"]:
                    output = "\n".join([("{}\n".format(i.text)) for i in self.items])
                else:
                    # human-readable format
                    output = "\n".join([("{}\n".format(i)) for i in self.items])

            if self.vargs["output"] is not None:
                # write to file
                try:
                    with io.open(self.vargs["output"], "w", encoding="utf-8") as f:
                        f.write(output)
                except IOError:
                    self.error("Unable to write output file. Please check that the path is correct and that you have write permission on it.")
            elif self.vargs["info"]:
                # print some info about the extraction
                self.print_stdout("Books with annotations or highlights: {}".format(len(enum_books)))
                if not self.vargs["list"]:
                    self.print_stdout("Total annotations and/or highlights:  {}".format(len(items)))
            else:
                # write to stdout
                try:
                    self.print_stdout(output)
                except UnicodeEncodeError:
                    self.print_stdout(output.encode("ascii", errors="replace"))

    def get_books(self):
        """
        Returns a list of tuple, with volumeid and Book instance.
        """
        if not self.books:
            self.books = [(d[0], Book(d)) for d in self.query(self.QUERY_BOOKS)]
        return self.books

    def get_book_by_id(self, bookid):
        """
        Returns a book by it's book id.
        """
        return self.books[int(bookid) - 1][1]

    def get_book_with_items_by_index(self, book_idx):
        """
        Returns a book by index and its items, in a tuple.
        """
        try:
            book = self.books[book_idx][1]
            filtered_items = [i for i in self.items if i.volumeid == book.volumeid]
            return (book, filtered_items)
        except Exception:
            self.error("Book not found at index.")

    def run_server(self):
        """
        Starts the server.
        """
        app.run()

    def list_to_markdown(self, books):
        """
        Convert the given Item data into a well-formed Markdown string.
        """
        output = ""
        book = self.current_book(books)

        if book == None:
            # no books specified, so print list of books
            for (i, b) in books:
                output += b.to_markdown()
                # filter items of the current book
                filtered_items = [i for i in self.items if i.volumeid == b.volumeid]
                output += "".join([i.markdown() for i in filtered_items])
        else:
            output += book.to_markdown()
            output += "".join([i.markdown() for i in self.items])
        return output

    def list_to_csv(self, data):
        """
        Convert the given Item data into a well-formed CSV string.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        for d in data:
            try:
                writer.writerow(d)
            except UnicodeEncodeError:
                writer.writerow(tuple([(v.encode("ascii", errors="replace") if v is not None else "") for v in d]))
        return output.getvalue()

    def extract_books(self):
        """
        Return the list of books into two formats:
        a dict with ``{volumeId: Book}``,
        a list of pairs ``(int, Book)`` with the index starting at one.
        """
        books = self.get_books()
        ids, books = zip(*books)
        return dict(zip(ids, books)), list(enumerate(books, start=1))

    def volumeid_from_bookid(self, books):
        """
        Get the correct ``volumeid`` from the ``bookid``,
        that is, the index of the book
        as produced by the ``enumerate_books()``.
        """
        bookid = self.vargs["bookid"]
        try:
            return books[int(bookid) - 1][1].volumeid
        except:
            self.error("The bookid value must be an integer between 1 and {}".format(len(books)))

    def current_book(self, books):
        """
        Returns the current book.
        """
        bookid, booktitle = self.vargs["bookid"], self.vargs["book"]

        if (bookid is None) and (booktitle is not None):
            return None
        if bookid is not None:
            return self.get_book_by_id(bookid)
        if booktitle is not None:
            return filter(lambda i, b: b.title == booktitle, books)[0]

    def read_items(self, dict_books, enum_books):
        """
        Query the SQLite file, filtering Item objects as specified
        by the user.
        """
        # Creating a new Item with the relative Book for extract title+author coming from the other table
        items = [Item(d, dict_books.get(d[0])) for d in self.query(self.QUERY_ITEMS)]
        if len(items) == 0:
            return items
        if (self.vargs["bookid"] is not None) and (self.vargs["book"] is not None):
            self.error("You cannot specify both --book and --bookid.")
        if self.vargs["bookid"] is not None:
            items = [i for i in items if i.volumeid == self.volumeid_from_bookid(enum_books)]
        if self.vargs["book"] is not None:
            items = [i for i in items if i.title == self.vargs["book"]]
        if self.vargs["highlights_only"]:
            items = [i for i in items if i.kind == Item.HIGHLIGHT]
        if self.vargs["annotations_only"]:
            items = [i for i in items if i.kind == Item.ANNOTATION]
        return items

    def query(self, query):
        """
        Run the given query over the SQLite file.
        """
        db_path = self.vargs["db"]
        if not os.path.exists(db_path):
            self.error("Unable to read KoboReader.sqlite file. Please check that the path is correct and that you have permission to read it.")
        try:
            sql_connection = sqlite3.connect(db_path)
            sql_cursor = sql_connection.cursor()
            sql_cursor.execute(query)
            data = sql_cursor.fetchall()
            sql_cursor.close()
            sql_connection.close()
        except Exception as exc:
            self.error("Unexpected error reading your KoboReader.sqlite file: {}".format(exc))
        # NOTE the values are Unicode strings (str on python3) hence data is a list of tuples of Unicode strings
        return data


if __name__ == "__main__":
    book_manager = ExportKobo()
    book_manager.run()
