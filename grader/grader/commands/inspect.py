import logging
import shutil
import subprocess

from grader.models import Grader
from grader.utils.config import require_grader_config

logger = logging.getLogger(__name__)

help = "Inspect a graded submission's container."


def setup_parser(parser):
    parser.add_argument('assignment',
                        help='Name of the assignment which the user has a '
                             'graded submission for.')
    parser.add_argument('student_id',
                        help='Inspect submission belonging to this student.')
    parser.add_argument('--user',
                        help="Linux user to inspect as")
    parser.set_defaults(run=run)


@require_grader_config
def run(args):
    g = Grader(args.path)
    a = g.get_assignment(args.assignment)

    if args.student_id not in a.submissions_by_user:
        logger.error("User does not have a graded submission available.")
        return

    user_submissions = a.submissions_by_user[args.student_id]
    id = None
    # If they have multiple submissions, make them choose
    if len(user_submissions) > 1:
        i = 1
        print("Index\tCreated")
        for s in user_submissions:
            info = a.docker_cli.inspect_container(s.full_id)
            print("{0}\t{1}".format(i, info['Created']))
            i += 1
        choice = -1
        while choice < 0 or choice >= len(user_submissions):
            choice = input("Please enter your selection: ")
            try:
                choice = int(choice)-1
            except:
                choice = -1

        id = user_submissions[choice].full_id
    else:
        id = user_submissions[0].full_id

    shell = a.gradesheet.config.get('shell', '/bin/bash')

    # Start container, run exec, stop container
    logger.info("Starting container {0}".format(id))
    a.docker_cli.start(container=id)

    command = [shutil.which("docker"), "exec", "-it"]
    if args.user:
        command.extend(["-u", args.user])

    command.extend([id, shell])
    subprocess.call(command)

    logger.info("Stopping container {0}".format(id))
    a.docker_cli.stop(container=id)