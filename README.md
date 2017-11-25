# FileFinder-CSEC475-2171-Alvarado-Daniels-Singh

A tool that can find a deleted file on an NTFS disk and recover them for a user.

## Prerequisites

FileFinder simply requires [Python 2.7+](https://www.python.org/) to be installed. In order
to read raw data from the disk, the user must have administrative access to the machine
FileFinder will be run on.

Please note that FileFinder only runs on Windows. Although Linux can use NTFS formatted disks,
FileFinder does not support it. Feel free to add Linux functionality with a 
[pull request](https://github.com/TRDan6577/FileFinder-CSEC475-2171-Alvarado-Daniels-Singh/pulls)!
=)

## How to use it

Open your favorite command line utility on Windows and navigate to the directory FileFinder is
stored in. Then simply run it.

`C:\User\myusername> python FileFinder.py`

When prompted, enter the name of the file you wish to find (including the file extension) and
wait. It should take less time to find your file than it would for you to rewrite your file
(or, to put it simply, it should take a couple seconds). 

Also, it's important to note that if you're trying to recover the file and you've just 
downloaded FileFinder, there's a decent chance you just permanently lost your file. The cool
thing about Python - among other things - is that it's an interpreted language. That means
you can copy the code to your clipboard and paste it into your interpreter (provided you
already have Python 2.7+ and an interpreter installed) and FileFinder won't be written
to disk - just to RAM.

## Caveats/Issues

None, the code is perfect.

But in a much more real sense: 
* If you're currently running any programs from the disk you
lost the file on, it's likely your file is already gone. For example, when I delete a
file and then try to find it while Google Chrome is running, I am unsuccessful in recovering
the file. I have no such issues when I try to recover a file from an NTFS formatted USB flash
drive.
* If you attempt to recover a file from a small NTFS formatted USB drive, the current method
fails to read 10,000 records, but works for smaller amounts such as 1,000 records. Permanently
using 1,000 as the default number of records to read slows the file search considerably on
larger drive so that is not a solution to this issue.

## Future Plans

* Because most people delete files from the recycle bin and don't permanently delete them using
Shift + delete, adding support for finding files that were first moved to the recycle bin
and *then* deleted would be a huge plus.
* Add options to search a different disk (other than the C: drive)
* Improve speed by checking to see if the file is marked for deletion before checking the
$FILE_NAME section.

## Resources

HUGE shout-out to [ntfs.com](http://ntfs.com) and this
[ntfs disk forensics site](http://www.cse.scu.edu/~tschwarz/coen252_07Fall/Lectures/NTFS.html).

## Contributers
Joncarlo Alvarado
Thomas Daniels
