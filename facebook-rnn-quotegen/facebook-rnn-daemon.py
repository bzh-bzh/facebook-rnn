import subprocess
import syslog
import signal
import traceback
import datetime

from gcloud import datastore
import fluent.sender
import fluent.event

from retrying import retry


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


# replace key in a string with the value
def replace_all(text, dic):
    for key, value in dic.items():
        text = text.replace(key, value)
    return text


def report(exception):
    data = {'message': '{0}'.format(exception), 'serviceContext': {'service': 'myapp'}}
    fluent.event.Event('errors', data)


@retry(stop_max_attempt_number=100, wait_exponential_multiplier=1000, wait_exponential_max=10000)
def datastore_put(client, entity):
    client.put(entity)


def main():
    killer = GracefulKiller()
    fluent.sender.setup('myapp', host='localhost', port=24224)

    client = datastore.Client("facebook-rnn")

    syslog.openlog()

    # arguments for the sample.lua command
    checkpoint_file = "cv/checkpoint_6650.t7"
    sampling_algo_arguments = ["th", "sample.lua", "-checkpoint", checkpoint_file, "-gpu", "-1", "-temperature", "0.7"]

    # censor the names of my friends
    names_censoring = {}
    while True:
        try:
            # run the command and capture its output
            sampling_process = subprocess.Popen(sampling_algo_arguments, stdout=subprocess.PIPE)
            sampling_output = sampling_process.communicate()[0]

            # convert from byte-string to unicode
            sampling_output = sampling_output.decode("utf-8")

            sampling_output = replace_all(sampling_output, names_censoring)

            # split the string by newlines
            sampling_output_list = sampling_output.splitlines()
            # remove the last, incomplete line
            sampling_output_list.remove(sampling_output_list[-1])

            for line in sampling_output_list:
                # 1-character messages are boring, and datastore limits to <1500 bytes.
                if (len(line) > 1) and (len(line) < 300) and (line != "None"):
                    message = datastore.Entity(client.key("Message"))
                    message.update({
                        "text": line,
                        "created": datetime.datetime.utcnow(),
                        "length": len(line)
                    })
                    datastore_put(client, message)

            if killer.kill_now:
                # kill any subprocesses that may be running
                sampling_process.terminate()
                syslog.syslog("Facebook RNN: Received SIGTERM/SIGKILL: stopping everything and shutting down.")
                syslog.closelog()
                break
        except Exception:
            report(traceback.format_exc())
            break


if __name__ == '__main__':
    main()
