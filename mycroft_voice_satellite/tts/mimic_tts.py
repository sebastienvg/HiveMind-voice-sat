# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import subprocess
from time import time
from mycroft_voice_satellite.tts import TTSValidator, TTS
from jarbas_utils.log import LOG


class Mimic(TTS):
    def __init__(self, lang, config):
        super(Mimic, self).__init__(
            lang, config, MimicValidator(self), 'wav',
            ssml_tags=["speak", "ssml", "phoneme", "voice", "audio", "prosody"]
        )
        self.dl = None
        self.clear_cache()
        self.bin = self.config.get("bin")
        if not self.bin:
            # Search for mimic on the path
            import distutils.spawn
            self.bin = distutils.spawn.find_executable("mimic")

    def modify_tag(self, tag):
        for key, value in [
            ('x-slow', '0.4'),
            ('slow', '0.7'),
            ('medium', '1.0'),
            ('high', '1.3'),
            ('x-high', '1.6'),
            ('speed', 'rate')
        ]:
            tag = tag.replace(key, value)
        return tag

    @property
    def args(self):
        """ Build mimic arguments. """
        voice = self.voice

        args = [self.bin, '-voice', voice, '-psdur', '-ssml']

        stretch = self.config.get('duration_stretch', None)
        if stretch:
            args += ['--setf', 'duration_stretch=' + stretch]
        return args

    def get_tts(self, sentence, wav_file):
        #  Generate WAV and phonemes
        phonemes = subprocess.check_output(self.args + ['-o', wav_file,
                                                        '-t', sentence])
        return wav_file, phonemes.decode()

    def viseme(self, output):
        visemes = []
        start = time()
        pairs = str(output).split(" ")
        for pair in pairs:
            pho_dur = pair.split(":")  # phoneme:duration
            if len(pho_dur) == 2:
                visemes.append((VISIMES.get(pho_dur[0], '4'),
                                float(pho_dur[1])))
        return visemes


class MimicValidator(TTSValidator):
    def __init__(self, tts):
        super(MimicValidator, self).__init__(tts)

    def validate_lang(self):
        # TODO: Verify version of mimic can handle the requested language
        pass

    def validate_connection(self):
        try:
            subprocess.call([BIN, '--version'])
        except Exception:
            LOG.info("Failed to find mimic at: " + BIN)
            raise Exception(
                'Mimic was not found. Run install-mimic.sh to install it.')

    def get_tts_class(self):
        return Mimic


# Mapping based on Jeffers phoneme to viseme map, seen in table 1 from:
# http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.221.6377&rep=rep1&type=pdf
#
# Mycroft unit visemes based on images found at:
# http://www.web3.lu/wp-content/uploads/2014/09/visemes.jpg
#
# Mapping was created partially based on the "12 mouth shapes visuals seen at:
# https://wolfpaulus.com/journal/software/lipsynchronization/

VISIMES = {
    # /A group
    'v': '5',
    'f': '5',
    # /B group
    'uh': '2',
    'w': '2',
    'uw': '2',
    'er': '2',
    'r': '2',
    'ow': '2',
    # /C group
    'b': '4',
    'p': '4',
    'm': '4',
    # /D group
    'aw': '1',
    # /E group
    'th': '3',
    'dh': '3',
    # /F group
    'zh': '3',
    'ch': '3',
    'sh': '3',
    'jh': '3',
    # /G group
    'oy': '6',
    'ao': '6',
    # /Hgroup
    'z': '3',
    's': '3',
    # /I group
    'ae': '0',
    'eh': '0',
    'ey': '0',
    'ah': '0',
    'ih': '0',
    'y': '0',
    'iy': '0',
    'aa': '0',
    'ay': '0',
    'ax': '0',
    'hh': '0',
    # /J group
    'n': '3',
    't': '3',
    'd': '3',
    'l': '3',
    # /K group
    'g': '3',
    'ng': '3',
    'k': '3',
    # blank mouth
    'pau': '4',
}