#!/usr/bin/env python3
#--------------------------------------------------------------------
# TTTT: TEA Text Transformer Terminal
#--------------------------------------------------------------------
# TEA, which is the Transforming Executable Alphabet language is implemented here
# using the Python programming language as the base/host language.
#--------------------------------------------------------------------
# The original/historically older TEA implementation is found in the TTTT Android app
# accessible via https://bit.ly/grabteas
#
# This commandline implementation of the TTTT is meant to extend the
# access of TEA to all major operating systems, by creating a standalone
# TEA interpreter that can be utilized in scripts, standalone programs
# and/or on the commandline.
#---------------------------------------------------------------------
# IDEATING IMPLIMENTING ARCHITECT: Joseph Willrich Lutalo (jwl@nuchwezi.com, joewillrich@gmail.com) C.M.R.W the nu ancient psychonaut ufora
# --- Please don't bother me with so much mail or calls, am usually busy thinking
#---------------------------------------------------------------------


import sys, os, subprocess
import urllib.request, urllib.parse
import re
import random
import argparse

DEBUG = True

#==================== CLI TTTT Design ================================
"""

echo INPUT | tttt

INPUT is considered to be a valid TEA program (possibly already containing its input), and is executed as such

Or with

echo INPUT | tttt -c CODE

Where INPUT is treated as input data and the TEA program is read from the string CODE

Or with

echo INPUT | tttt -fc FCODE

Where INPUT is treated as input data and the TEA program is read from the file path FCODE

Or with

tttt -i INPUT -c CODE

Where INPUT is treated as input data and the TEA program is read from the string CODE

Or with

tttt -i INPUT -fc FCODE

Where INPUT is treated as input data and the TEA program is read from the file path FCODE

Or with

tttt -fi INPUT -fc FCODE

Where INPUT is treated as data input file path and the TEA program is read from the file path FCODE

In all situations, the TTTT interpreter executes the available TEA program on the available input data and outputs the final result via standard output, and does nothing else but quit.
"""

class TEA_RunTime:
    #-------------------------------------
    # CONSTANTS
    #-------------------------------------
    # Important CONSTANTS for the runtime
    OBSCURE_RC_NL = "=NL=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=NL="
    OBSCURE_RC_COM = "=COM=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=COM="
    OBSCURE_RC_TID = "=TID=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=TID="
    TID = "|"
    #NL = "\n"
    NL = os.linesep
    COMH = "#"
    TCD = ":"
    TIPED = ":"
    RETEASTRING1 = r'\{.*?\}'
    RETEASTRING2 = r'"[^"]*?"'
    RETEAPROGRAM = r'([a-zA-Z]\*?!?:.*(:.*)*\|?)+(#.*)*'
    RETI = r'[ ]*?[a-zA-Z]\*?!?:.*?'
    SINGLE_SPACE_CHAR = " "
    ALPHABET = "abcdefghijklmnopqrstuvwxyz"
    EXTENDED_ALPHABET = ALPHABET + SINGLE_SPACE_CHAR
    RE_WHITE_SPACE = r'\s+'
    RE_WHITE_SPACE_N_PUNCTUATION = r'[\s\W]+'
    GLUE = SINGLE_SPACE_CHAR
    EMPTY_STR = ""
    vDEFAULT_VAULT = EMPTY_STR

# Function to replace newlines with OBSCURE Pattern
    def maskTEASTRING(self, mObj):
        return mObj.group().replace('\n', self.OBSCURE_RC_NL).replace('#',self.OBSCURE_RC_COM).replace('|',self.OBSCURE_RC_TID)

# Clean TEA CODE:
# Essentially, eliminate all TEA Opaque Lines:
# - TEA Comments
# - Non-TEA Instruction Lines
# and put each TI on its own line, with any leading whitespace removed
    def clean_TSRC(self, tsrc):
        if len(tsrc) == 0:
            return tsrc
        # remove trailing whitespace
        _tsrc = tsrc.strip()
        # first, fold multi-line TIL strings
        _tsrc = re.sub(self.RETEASTRING1, self.maskTEASTRING, _tsrc, flags=re.DOTALL)
        _tsrc = re.sub(self.RETEASTRING2, self.maskTEASTRING, _tsrc, flags=re.DOTALL)
        # remove all TEA comments
        reTCOM = re.compile("#[^\n]*")
        _tsrc = re.sub(reTCOM,"",_tsrc)
        # first, split by newline
        _tsrc_lines = _tsrc.split(self.NL)
        _tils = []
        # process multiple tils on same line
        for l  in _tsrc_lines:
            # split a line by TID
            if self.TID in l:
                _tis = l.split(self.TID)
                _tils.extend(_tis)
            else:
                _tils.append(l)
        _tsrc_lines = _tils
        if TEA_RunTime.DEBUG:
            print(f"#{len(_tsrc_lines)} of {(_tsrc_lines)}")
        reTI = re.compile(self.RETI)
        # remove all non-TIL lines
        _tsrc_til_only = [l.lstrip() for l in _tsrc_lines if reTI.match(l)]
        if TEA_RunTime.DEBUG:
            # reverse string masking...
            _tsrc_til_only_show = [l.
                    replace(self.OBSCURE_RC_NL,self.NL)
                    .replace(self.OBSCURE_RC_COM,self.COMH)
                    .replace(self.OBSCURE_RC_TID,self.TID) for l in _tsrc_til_only]
            print(f"##{len(_tsrc_til_only_show)} of {(_tsrc_til_only_show)}")
        _tsrc = self.NL.join(_tsrc_til_only)
        return _tsrc

# Pre-process TEA CODE
    def pre_process_TSRC(self, tsrc):
# for now, trim all leading and trailing white space
            return tsrc.strip()

# Validate TEA CODE:
# Essentially, check if:
# - Code contains at least one valid TEA Instruction Line:
# ([a-zA-Z]!?*?:.*(:.*)*|?)+(#.*)*
    def validate_TSRC(self, tsrc):
        reTEAPROGRAM = re.compile(TEA_RunTime.RETEAPROGRAM)
        errors = []
        _tsrc = tsrc.strip()
        isValid = False if len(_tsrc) == 0 else True
        if not isValid:
            errors.append("[ERROR] TEA Source is Empty!")
            return isValid, errors
        isValid = re.search(reTEAPROGRAM,_tsrc) is not None
        if not isValid:
            errors.append("[ERROR] TEA Source is INVALID!")
            return isValid, errors
        else:
            return isValid, errors

    def _parse_tea_code(self, code):
        otil = []
        tsrc = self.pre_process_TSRC(code)
        isTSRCValid,errors = self.validate_TSRC(tsrc)
        if not isTSRCValid:
            if TEA_RunTime.DEBUG:
                print("TEA CODE ERRORS FOUND:\n%s" % "\n".join(errors))
            return
        onlyTILTSRC = self.clean_TSRC(tsrc)
        if TEA_RunTime.DEBUG:
            print(f"CLEAN TEA CODE TO PROCESS:\n{onlyTILTSRC}")

        otil = onlyTILTSRC.split(self.NL)
        return otil

    def _parse_labelblocks(self, otil, initial_labelblocks = {}):
        TI_index = 0
        labelblocks = initial_labelblocks
        for i in otil:
            if i.upper().startswith("L"):
                params = i.split(TEA_RunTime.TCD)
                for lBlockName in params[1:]:
                    cleanlBlockName = lBlockName.strip()
                    if cleanlBlockName in labelblocks:
                        if cleanlBlockName not in initial_labelblocks:
                            if TEA_RunTime.DEBUG:
                                print(f"[ERROR] Instruction {i} trying to duplicate an Existenting Block Name [{cleanlBlockName}]")
                                print(f"[INFO] Current L-BLOCKS: \n{labelblocks}")
                            raise ValueError("[SEMANTIC ERROR] ATTEMPT to DUPLICATE EXISTING BLOCK LABEL")
                        else:
                            pass # allow to override
                    labelblocks[cleanlBlockName] = TI_index + 1 # so we ref next instruction in program, after the label
            TI_index += 1


        if TEA_RunTime.DEBUG:
            print(f"\n---<< EXTRACTED TEA LABEL BLOCKS:\n{labelblocks}\n")

        return labelblocks


    def run_tttt(self, _process_cli = False, _tsrc=None, _ai=None, _debug=False):
        self.DEBUG = _debug


        INPUT = _ai #shall either be read from stdin or from the val to -i or -fi
        CODE = _tsrc #shall either be from INPUT or from the val to -c or -fc
        HasSTDIN = False
        STDINPUT = None
        STDIN_AS_CODE = False
        VAULTS = {}
        # we shall store label block pointers as such:
        #    label_name: label_position + 1
        #    such that, jumping to label_name allows us to
        #    proceed execution from instruction at index label_position +1
        LABELBLOCKS = {}
        ATPI = 0 # Active TI POSITION INDEX

# in case data was input via STDIN (such as via a pipe)
        if os.isatty(sys.stdin.fileno()):
            INPUT = None
            STDINPUT = None
        else:
            STDINPUT = os.linesep.join(sys.stdin.readlines())
            HasSTDIN = True



#-----------------------------
# VAULT/MEMORY utils
#-----------------------------

        def vault_store(vNAME, vVAL):
            VAULTS[vNAME] = vVAL
            if TEA_RunTime.DEBUG:
                print(f"-- [INFO] Wrote VAULT[{vNAME} = [{vVAL}]]")

        def vault_get(vNAME):
            if not (vNAME in VAULTS):
                if TEA_RunTime.DEBUG:
                    print(f"[ERROR] Instruction trying to access DEFAULT VAULT before it is set!")
                raise ValueError("[MEMORY ERROR] ATTEMPT to ACCESS unset DEFAULT VAULT")
            else:
                if TEA_RunTime.DEBUG:
                    print(f"-- [INFO] Reading VAULT[{vNAME}]")
            return VAULTS[vNAME]


#-----------------------------
# UTILS
#-----------------------------

# Function to read all lines from a file
        def read_file(file_path):
            try:
                with open(file_path, 'r') as file:
                    return TEA_RunTime.NL.join(file.readlines())
            except BaseException:
                return None

        # reverse TEA String Masking
        def unmask_str(val):
            return val.replace(TEA_RunTime.OBSCURE_RC_NL,TEA_RunTime.NL).replace(TEA_RunTime.OBSCURE_RC_COM,TEA_RunTime.COMH).replace(TEA_RunTime.OBSCURE_RC_TID,TEA_RunTime.TID)

        # Extract a string from a TEA expression
        def extract_str(val):
            if val.startswith("{") and val.endswith("}"):
                val = val.lstrip("{").rstrip("}")
                return unmask_str(val)
            if val.startswith("\"") and val.endswith("\""):
                val = val.lstrip("\"").rstrip("\"")
                return unmask_str(val)
            return unmask_str(val)

        def util_anagramatize_words(val):
            parts = re.split(TEA_RunTime.RE_WHITE_SPACE, val)
            lparts = random.sample(parts, len(parts))
            return TEA_RunTime.GLUE.join(lparts)

        def util_anagramatize_chars(val):
            parts = list(val)
            return TEA_RunTime.EMPTY_STR.join(random.sample(list(parts), len(parts)))

        def util_unique_chars(val):
            unique_chars = ""
            for char in val:
                if char not in unique_chars:
                    unique_chars += char
            return unique_chars

        def util_mirror_words(val):
            parts = re.split(TEA_RunTime.RE_WHITE_SPACE, val)
            lparts = parts[::-1]
            return TEA_RunTime.GLUE.join(lparts)

        def util_mirror_chars(val):
            return TEA_RunTime.EMPTY_STR.join(list(reversed(val)))

        def util_gen_rand(limit, ll=0):
            return limit if limit == ll else random.randint(int(ll), int(limit))

        def util_sort_words(val):
            parts = re.split(TEA_RunTime.RE_WHITE_SPACE, val)
            lparts = sorted(parts)
            return TEA_RunTime.GLUE.join(lparts)

        def util_sort_chars(val):
            lparts = sorted(val)
            return TEA_RunTime.EMPTY_STR.join(lparts)

        def util_gen_permutations(val, glue=TEA_RunTime.GLUE, limit=100):
            iteration, iteration_limit = 0, limit * 2
            instance_limit = util_gen_rand(limit,ll=1)
            permutations = []
            while len(permutations) < instance_limit:
                if iteration > iteration_limit:
                    break
                else:
                    iteration += 1
                vAnagram = util_anagramatize_chars(val)
                if vAnagram in permutations:
                    continue
                else:
                    permutations.append(vAnagram)
            return glue.join(permutations)


        def util_gen_rand_string(size=None, alphabet=TEA_RunTime.EXTENDED_ALPHABET, glue=TEA_RunTime.GLUE):
            instance_limit = util_gen_rand(int(size) if size is not None else 100,ll=1)
            if size is not None:
                instance_limit = size
            return TEA_RunTime.EMPTY_STR.join(random.choice(alphabet) for _ in range(instance_limit))

        def util_braille_projection1(val):
            # Define the pattern for non-whitespace characters
            rNonWhiteSpace = r'\S'
            # remove all non-whitespace characters
            val = re.sub(rNonWhiteSpace, TEA_RunTime.EMPTY_STR, val)
            # pattern [ \t\r\f\v] matches spaces, tabs, carriage returns, form feeds, and vertical tabs, but not newlines.
            rWhiteSpace = r'[ \t\r\f\v]'
            # replace all white space except newline with full-stop
            val = re.sub(rWhiteSpace, '.', val)
            return val

        def util_braille_projection2(val):
            # Define the pattern for non-whitespace characters
            rNonWhiteSpace = r'\S'
            # Replace all non-whitespace characters
            val = re.sub(rNonWhiteSpace, '#', val)
            # replace all white space except newline with full-stop
            rWhiteSpace = r'[ \t\r\f\v]'
            val = re.sub(rWhiteSpace, '.', val)
            val = val.replace('#', TEA_RunTime.SINGLE_SPACE_CHAR)
            return val

        def util_salt_string(val, salt, injection_limit = None, llimit=None):
            l_val = len(val)
            if l_val == 0:
                return val # nothing to salt
            l_val = len(val) + 1 # so the salt can also become a suffix
            u_limit = injection_limit if (injection_limit is not None) and (injection_limit < l_val) else l_val
            injection_index = util_gen_rand(u_limit, ll=llimit or 0)
            if TEA_RunTime.DEBUG:
                print(f"Salting {val} of len[{len(val)}] at index[{injection_index}]--> {val[:injection_index]} + {salt} + {val[injection_index:]}")
            salted_val = str(val[:injection_index] + salt + val[injection_index:])
            return salted_val

        def util_unsalt_string(val, llimit=None, deletion_limit = None, salt_pattern=None):
            l_val = len(val)
            if l_val == 0:
                return val # nothing to unsalt
            if salt_pattern is None:
                deletion_index = util_gen_rand(l_val)
                unsalted_val = str(val[:deletion_index] + val[deletion_index + 1:])
                return unsalted_val
            else:
                # get all sections matching pattern in val
                matches = list(re.finditer(salt_pattern, val))
                l_matches = len(matches)
                if l_matches == 0:
                    return val # nothing to unsalt
                d_limit = deletion_limit if (deletion_limit is not None) and (deletion_limit < l_matches) else l_matches
                deletion_index = util_gen_rand(d_limit, ll=llimit or 0)
                # Get the start and end positions of the chosen match
                start, end = matches[deletion_index].span()
                if TEA_RunTime.DEBUG:
                    print(f"UnSalting {val} of len[{len(val)}] between index[{start} and {end}]--> {val[:start]} + {val[end:]}")
                unsalted_val = val[:start] + val[end:]
                return unsalted_val

# TEA triangular reduction
        def util_triangular_reduction(val):
            if TEA_RunTime.DEBUG:
                print(f"--[util]-| Applying Transform: LM-TR to [{val}]")
            lines = []
            for i in range(len(val)):
                lines.append(val[i:])
            return TEA_RunTime.NL.join(lines)


# TEA right-most triangular reduction
        def util_rightmost_triangular_reduction(val):
            if TEA_RunTime.DEBUG:
                print(f"--[util]-| Applying Transform: RM-TR to [{val}]")
            lines = []
            for i in range(len(val)):
                lines.append(val[:(len(val)-i)])
            return TEA_RunTime.NL.join(lines)

        def util_unique_projection_words(val):
            if TEA_RunTime.DEBUG:
                print(f"--[util]-| Computing Unique Word Projection for [{val}]")
            words = val.split(TEA_RunTime.SINGLE_SPACE_CHAR)
            l_words = len(words)
            if l_words <= 1:
                return val
            unique_words = list(set(words))
            tally = [(w,words.count(w)) for w in unique_words]
            tally = sorted(tally,key=lambda votes:votes[1], reverse=True)
            if TEA_RunTime.DEBUG:
                print(f"--[util]-| Unique Word Tally [{tally}]")
            return TEA_RunTime.GLUE.join([w[0] for w in tally])


        def util_unique_projection_chars(val):
            if TEA_RunTime.DEBUG:
                print(f"--[util]-| Computing Unique Character Projection for [{val}]")
            chars = list(val)
            l_chars = len(chars)
            if l_chars <= 1:
                return val
            unique_chars = list(set(chars))
            tally = [(w,chars.count(w)) for w in unique_chars]
            tally = sorted(tally,key=lambda votes:votes[1], reverse=True)
            if TEA_RunTime.DEBUG:
                print(f"--[util]-| Unique Char Tally [{tally}]")
            return TEA_RunTime.EMPTY_STR.join([w[0] for w in tally])


        def util_system_b(cmd, cmdData, show_errors=False):
            result = None
            try:
                # Combine the command and data
                full_command = f"{cmd} {cmdData} 2> /dev/null"
                # Execute the command
                with os.popen(full_command) as process:
                    result = process.read()
                    if TEA_RunTime.DEBUG:
                        print(f"---[SYSTEM CMD CALL:B]: \n\tCMD: {cmd}\n\tCMDDATA: {cmdData}\n\tRESULT: {result}")
            except Exception as error:
                if TEA_RunTime.DEBUG:
                    print(f"***[SYSTEM CMD EXCEPTION]: \n\tCMD: {cmd}\n\tCMDDATA: {cmdData}\n\tERROR: {error}")
                if show_errors:
                    result = f"[ERROR]: {error}"

            return result.strip() if result is not None else result


        def util_system(cmd, cmdData, show_errors=False):
            result = None
            try:
                res = util_system_b(cmd, cmdData, show_errors=show_errors)
                if res is not None:
                    return res

                # Execute the command with the data
                process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate(input=cmdData.encode())

                # Check for errors
                if process.returncode != 0:
                    error = stderr.decode()
                    if TEA_RunTime.DEBUG:
                        print(f"***[SYSTEM CMD ERROR]: \n\tCMD: {cmd}\n\tCMDDATA: {cmdData}\n\tERROR: {error}")
                        print(f"***[SYSTEM CMD]: Attempting alternative call..")

                    # re-try call-type B without any data...
                    res = util_system_b(cmd, None, show_errors=show_errors)
                    if res is not None:
                        result = res
                    else:
                        if show_errors:
                            result = f"[ERROR]: {error}"
                else:
                    result = stdout.decode()
                    if TEA_RunTime.DEBUG:
                        print(f"---[SYSTEM CMD CALL:A]: \n\tCMD: {cmd}\n\tCMDDATA: {cmdData}\n\tRESULT: {result}")

            except Exception as error:
                if TEA_RunTime.DEBUG:
                    print(f"***[SYSTEM CMD EXCEPTION]: \n\tCMD: {cmd}\n\tCMDDATA: {cmdData}\n\tERROR: {error}")
                if show_errors:
                    result = f"[ERROR]: {error}"
            return result.strip() if result is not None else result


        def util_fix_url(url):
            if not (url.startswith("http")):
                return f"http://{url}"
            return url

        def util_web_get(url, data=None):
            result = None
            try:

                full_url = url
                if data is not None:
                    if isinstance(data, dict):
                        # Encode the data as query parameters
                        query_string = urllib.parse.urlencode(data)
                        full_url = f"{url}?{query_string}"

                with urllib.request.urlopen(full_url) as response:
                    # Read the content and decode it to a string
                    result = response.read().decode('utf-8')
            except Exception as error:
                _result = util_web_get(util_fix_url(url), data=data)
                if _result is not None:
                    result = _result
                else:
                    result = f"[ERROR]: {error}"
            return result.strip() if result is not None else result


        def util_web_post(url, data=None):
            result = None
            try:
                request = None
                encoded_data = None

                if isinstance(data, dict):
                    if data is not None:
                        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
                else:
                    encoded_data = data.encode('utf-8')
                    request = urllib.request.Request(url, data=encoded_data, method='POST')
                    # Set the appropriate header for form data
                    request.add_header('Content-Type', 'application/x-www-form-urlencoded')

                request = urllib.request.Request(url, data=encoded_data)

                with urllib.request.urlopen(request) as response:
                    # Read the content and decode it to a string
                    result = response.read().decode('utf-8')

            except Exception as error:
                _result = util_web_post(util_fix_url(url), data=data)
                if _result is not None:
                    result = _result
                else:
                    result = f"[ERROR]: {error}"
            return result.strip() if result is not None else result


        def util_execute_tea(tsrc, ai):
            if (tsrc is None) or (len(tsrc) == 0):
                return ai

            if TEA_RunTime.DEBUG:
                print(f"[INFO] TEA EXEC:\n\tTSRC: [{tsrc}]\n\tAI: [{ai}]\n")

            e_runtime = TEA_RunTime()
            e_output = e_runtime.run_tttt(_process_cli=False, _tsrc=tsrc, _ai=ai, _debug=TEA_RunTime.DEBUG)
            return e_output


        def util_inject_tea(tsrc, otil, injection_position, label_blocks):
            if (tsrc is None) or (len(tsrc) == 0):
                return otil, label_blocks, injection_position

            if TEA_RunTime.DEBUG:
                print(f"[INFO] TEA INJECTION:\n\tTSRC: [{tsrc}]\n\t@ATPI: [{injection_position}]\n")

            e_runtime = TEA_RunTime()
            e_otil = e_runtime._parse_tea_code(tsrc)
            e_otil = otil[:injection_position] + e_otil + otil[injection_position+1:] # update instructions list
            e_label_blocks = e_runtime._parse_labelblocks(e_otil, initial_labelblocks = label_blocks)

            return e_otil, e_label_blocks, injection_position

#-----------------------------
# TAZ Implementation
#-----------------------------
        def process_a(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "A":
                input_str = tpe_str if len(tpe_str) > 0 else ai
                io = util_anagramatize_words(input_str)
            if tc == "A!":
                input_str = tpe_str if len(tpe_str) > 0 else ai
                io = util_anagramatize_chars(input_str)
            if tc == "A*":
                input_str = vault_get(tpe_str) if len(tpe_str) > 0 else ai
                io = util_anagramatize_words(input_str)
            if tc == "A*!":
                input_str = vault_get(tpe_str) if len(tpe_str) > 0 else ai
                io = util_anagramatize_chars(input_str)
            return io


        def process_b(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "B":
                input_str = tpe_str if len(tpe_str) > 0 else ai
                io = util_unique_chars(input_str)
            if tc == "B!":
                input_str = tpe_str if len(tpe_str) > 0 else ai
                io = TEA_RunTime.EMPTY_STR.join(sorted(util_unique_chars(input_str)))
            if tc == "B*":
                input_str = vault_get(tpe_str) if len(tpe_str) > 0 else ai
                io = util_unique_chars(input_str)
            if tc == "B*!":
                input_str = vault_get(tpe_str) if len(tpe_str) > 0 else ai
                io = TEA_RunTime.EMPTY_STR.join(sorted(util_unique_chars(input_str)))
            return io


        def process_c(ti, ai):
            io = TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()

            if tc == "C":
                pass
            if tc == "C!":
                for vault in VAULTS:
                    VAULTS[vault] = TEA_RunTime.EMPTY_STR
            return io


        def process_d(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "D":
                dpatterns = tpe_str.split(TEA_RunTime.TIPED)
                for dp in dpatterns:
                    io = re.sub(dp, TEA_RunTime.EMPTY_STR, io)
            if tc == "D!":
                if len(tpe_str) == 0:
                    io = re.sub(TEA_RunTime.RE_WHITE_SPACE, TEA_RunTime.EMPTY_STR, io)
                else:
                    dpatterns = tpe_str.split(TEA_RunTime.TIPED)
                    dfilter = "|".join(dpatterns)
                    matches = re.findall(dfilter,io)
                    io = TEA_RunTime.GLUE.join(matches)
            return io


        def process_e(ti, ai, main_INSTRUCTIONS, main_ATPI, main_LABELBLOCKS):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)


            if TEA_RunTime.DEBUG:
                print(f"\n*******[ EXECUTING E-COMMAND ]\n")

            if tc == "E":
                if len(tpe_str) == 0:
                    e_Tsrc = io
                    e_ai = TEA_RunTime.EMPTY_STR
                    io = util_execute_tea(e_Tsrc, e_ai)
                else:
                    e_Tsrc = tpe_str
                    e_ai = io
                    io = util_execute_tea(e_Tsrc, e_ai)

            if tc == "E!":
                if len(tpe_str) == 0:
                    e_Tsrc = io
                    e_ai = TEA_RunTime.EMPTY_STR
                    e_INSTRUCTIONS, e_LABELBLOCKS, e_atpi = util_inject_tea(e_Tsrc, main_INSTRUCTIONS, main_ATPI, main_LABELBLOCKS)

                    return e_ai,e_atpi,e_INSTRUCTIONS,e_LABELBLOCKS

                else:
                    e_Tsrc = tpe_str
                    e_ai = io
                    e_INSTRUCTIONS, e_LABELBLOCKS, e_atpi = util_inject_tea(e_Tsrc, main_INSTRUCTIONS, main_ATPI, main_LABELBLOCKS)

                    return e_ai,e_atpi,e_INSTRUCTIONS,e_LABELBLOCKS

            if tc == "E*":
                if len(tpe_str) == 0:
                    if TEA_RunTime.DEBUG:
                        print(f"[ERROR] Instruction {ti} Invoked with Invalid Signature")
                    raise ValueError("[SEMANTIC ERROR] Invalid Instruction Signature")
                else:
                    vNAME = tpe_str
                    input_str = vault_get(vNAME)

                    e_Tsrc = input_str
                    e_ai = io
                    io = util_execute_tea(e_Tsrc, e_ai)

            if tc == "E*!":
                if len(tpe_str) == 0:
                    if TEA_RunTime.DEBUG:
                        print(f"[ERROR] Instruction {ti} Invoked with Invalid Signature")
                    raise ValueError("[SEMANTIC ERROR] Invalid Instruction Signature")
                else:
                    vNAME = tpe_str
                    input_str = vault_get(vNAME)
                    e_Tsrc = input_str
                    e_ai = io
                    e_INSTRUCTIONS, e_LABELBLOCKS, e_atpi = util_inject_tea(e_Tsrc, main_INSTRUCTIONS, main_ATPI, main_LABELBLOCKS)

                    return e_ai,e_atpi,e_INSTRUCTIONS,e_LABELBLOCKS

            if TEA_RunTime.DEBUG:
                print(f"\n*******[ FINISHED E-COMMAND ]\n")

            main_ATPI += 1 #move to next instruction if E: didn't already...
            return io,main_ATPI,main_INSTRUCTIONS,main_LABELBLOCKS


        def process_f(ti, ai, _ATPI):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "F":
                params = tpe_str.split(TEA_RunTime.TIPED)
                if len(params) == 0:
                    return io,_ATPI
                if len(params) == 1:
                    if TEA_RunTime.DEBUG:
                        print(f"[ERROR] Instruction {ti} Invoked with No Labels!")
                        print(f"--- L-BLOCK STATE: \n\t{LABELBLOCKS}")
                    raise ValueError(f"[ERROR] Fork Instruction {ti} Invoked with No Labels!")
                if len(params) == 2:
                    rtest = params[0]
                    tblock = params[1]
                    if not (tblock in LABELBLOCKS):
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} trying to access Non-Existent Block [{tblock}]")
                            print(f"--- L-BLOCK STATE: \n\t{LABELBLOCKS}")
                        raise ValueError("[CODE ERROR] ATTEMPT to ACCESS NON-EXISTENT BLOCK")
                    if (bool(re.search(rtest, io)) or (re.match(rtest, io)) or (rtest == io) or (rtest in io)):
                        _ATPI = LABELBLOCKS[tblock]
                    else:
                        _ATPI += 1
                    return io,_ATPI
                else:
                    rtest = params[0]
                    tblock = params[1]
                    fblock = params[2]
                    if not (tblock in LABELBLOCKS):
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} trying to access Non-Existent Block [{tblock}]")
                            print(f"--- L-BLOCK STATE: \n\t{LABELBLOCKS}")
                        raise ValueError("[CODE ERROR] ATTEMPT to ACCESS NON-EXISTENT BLOCK")
                    if not (fblock in LABELBLOCKS):
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} trying to access Non-Existent Block [{fblock}]")
                            print(f"--- L-BLOCK STATE: \n\t{LABELBLOCKS}")
                        raise ValueError("[CODE ERROR] ATTEMPT to ACCESS NON-EXISTENT BLOCK")
                    if (bool(re.search(rtest, io)) or (re.match(rtest, io)) or (rtest == io) or (rtest in io)):
                        _ATPI = LABELBLOCKS[tblock]
                    else:
                        _ATPI = LABELBLOCKS[fblock]
                    return io,_ATPI

            if tc == "F!":
                params = tpe_str.split(TEA_RunTime.TIPED)
                if len(params) == 0:
                    return io,_ATPI
                if len(params) == 1:
                    if TEA_RunTime.DEBUG:
                        print(f"[ERROR] Instruction {ti} Invoked with No Labels!")
                    raise ValueError(f"[ERROR] Fork Instruction {ti} Invoked with No Labels!")
                if len(params) == 2:
                    rtest = params[0]
                    tblock = params[1]
                    if not (tblock in LABELBLOCKS):
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} trying to access Non-Existent Block [{tblock}]")
                            print(f"--- L-BLOCK STATE: \n\t{LABELBLOCKS}")
                        raise ValueError("[CODE ERROR] ATTEMPT to ACCESS NON-EXISTENT BLOCK")
                    if not (bool(re.search(rtest, io)) or (re.match(rtest, io)) or (rtest == io) or (rtest in io)):
                        _ATPI = LABELBLOCKS[tblock]
                    else:
                        _ATPI += 1
                    return io,_ATPI
                else:
                    rtest = params[0]
                    tblock = params[1]
                    fblock = params[2]
                    if not (tblock in LABELBLOCKS):
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} trying to access Non-Existent Block [{tblock}]")
                            print(f"--- L-BLOCK STATE: \n\t{LABELBLOCKS}")
                        raise ValueError("[CODE ERROR] ATTEMPT to ACCESS NON-EXISTENT BLOCK")
                    if not (fblock in LABELBLOCKS):
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} trying to access Non-Existent Block [{fblock}]")
                            print(f"--- L-BLOCK STATE: \n\t{LABELBLOCKS}")
                        raise ValueError("[CODE ERROR] ATTEMPT to ACCESS NON-EXISTENT BLOCK")
                    if not (bool(re.search(rtest, io)) or (re.match(rtest, io)) or (rtest == io) or (rtest in io)):
                        _ATPI = LABELBLOCKS[tblock]
                    else:
                        _ATPI = LABELBLOCKS[fblock]
                    return io,_ATPI

            _ATPI += 1 #move to next instruction if fork didn't evaluate...
            return io,_ATPI


        def process_g(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "G":
                params = tpe_str.split(TEA_RunTime.TIPED)
                if len(params) == 0:
                    io = re.sub(TEA_RunTime.RE_WHITE_SPACE, TEA_RunTime.EMPTY_STR, io)
                if len(params) == 1:
                    glue = extract_str(params[0])
                    io = re.sub(TEA_RunTime.RE_WHITE_SPACE, glue, io)
                if len(params) == 2:
                    regex = params[1]
                    glue = extract_str(params[0])
                    io = re.sub(regex, glue, io)
            if tc == "G!":
                params = tpe_str.split(TEA_RunTime.TIPED)
                if len(params) == 0:
                    pass
                if len(params) == 1:
                    glue = extract_str(params[0])
                    io = re.sub(TEA_RunTime.RE_WHITE_SPACE_N_PUNCTUATION, glue, io)
            if tc == "G*":
                params = tpe_str.split(TEA_RunTime.TIPED)
                if len(params) < 3:
                    pass
                else:
                    glue = extract_str(params[0])
                    vaults = params[1:]
                    vals = []
                    for v in vaults:
                        vals.append(vault_get(v))
                    io = glue.join(vals)
            return io


        def process_h(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "H":
                if len(tpe_str) == 0:
                    io = TEA_RunTime.SINGLE_SPACE_CHAR.join(list(io))
                else:
                    regex = r'(?=' + tpe_str + ')'
                    parts = re.split(regex, io)
                    io = TEA_RunTime.SINGLE_SPACE_CHAR.join(parts)
            if tc == "H!":
                if len(tpe_str) == 0:
                    io = TEA_RunTime.NL.join(list(io))
                else:
                    regex = r'(?=' + tpe_str + ')'
                    parts = re.split(regex, io)
                    io = TEA_RunTime.NL.join(parts)
            if tc == "H*":
                params = tpe_str.split(TEA_RunTime.TIPED, maxsplit=2)
                if len(params) < 2:
                    pass
                else:
                    vault = params[0]
                    regex = params[1]
                    input_str = vault_get(vault)
                    io = TEA_RunTime.SINGLE_SPACE_CHAR.join(list(input_str))
            if tc == "H*!":
                params = tpe_str.split(TEA_RunTime.TIPED, maxsplit=2)
                if len(params) < 2:
                    pass
                else:
                    vault = params[0]
                    regex = params[1]
                    input_str = vault_get(vault)
                    regex = r'(?=' + regex + ')'
                    parts = re.split(regex, input_str)
                    io = TEA_RunTime.NL.join(parts)
            return io


        def process_i(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "I":
                if len(tpe_str) == 0:
                    pass
                else:

                    if (io is None) or (len(io) == 0):
                        io = tpe_str
            if tc == "I!":
                if len(tpe_str) == 0:
                    io = TEA_RunTime.EMPTY_STR
                else:
                    io = tpe_str
            return io


        def process_j(ti, ai, _ATPI):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "J":
                if len(tpe_str) == 0:
                    pass
                else:
                    jblock = tpe_str
                    if not (jblock in LABELBLOCKS):
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} trying to access Non-Existent Block [{jblock}]")
                        raise ValueError("[CODE ERROR] ATTEMPT to ACCESS NON-EXISTENT BLOCK")
                    _ATPI = LABELBLOCKS[jblock]
                    return io,_ATPI
            if tc == "J!":
                if len(tpe_str) == 0:
                    _ATPI = 0 # start of program
                    return io,_ATPI
                else:
                    pass

            _ATPI += 1 #move to next instruction if jump didn't evaluate...
            return io,_ATPI


        def process_k(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if io is None or len(io) == 0:
                return io

            if tc == "K":
                if len(tpe_str) == 0:
                    pass
                else:
                    regex = tpe_str
                    inputLines = io.split(NL)
                    keptLines = []
                    PATTERN = re.compile(regex)
                    for line in inputLines:
                        if (bool(re.search(PATTERN, line)) or (re.match(PATTERN, line)) or (PATTERN == line) or (PATTERN in line)):
                            keptLines.append(line)
                    io = TEA_RunTime.NL.join(keptLines)
            if tc == "K!":
                if len(tpe_str) == 0:
                    pass
                else:
                    regex = tpe_str
                    inputLines = io.split(NL)
                    keptLines = []
                    PATTERN = re.compile(regex)
                    for line in inputLines:
                        if not (bool(re.search(PATTERN, line)) or (re.match(PATTERN, line)) or (PATTERN == line) or (PATTERN in line)):
                            keptLines.append(line)
                    io = TEA_RunTime.NL.join(keptLines)

            if tc == "K*":
                params = tpe_str.split(TEA_RunTime.TIPED, maxsplit=2)
                if len(params) < 2:
                    pass
                else:
                    vault = params[0]
                    regex = params[1]
                    input_str = vault_get(vault)

                    inputLines = input_str.split(NL)
                    keptLines = []
                    PATTERN = re.compile(regex)
                    for line in inputLines:
                        if (bool(re.search(PATTERN, line)) or (re.match(PATTERN, line)) or (PATTERN == line) or (PATTERN in line)):
                            keptLines.append(line)
                    io = TEA_RunTime.NL.join(keptLines)
            if tc == "K*!":
                params = tpe_str.split(TEA_RunTime.TIPED, maxsplit=2)
                if len(params) < 2:
                    pass
                else:
                    vault = params[0]
                    regex = params[1]
                    input_str = vault_get(vault)

                    inputLines = input_str.split(NL)
                    keptLines = []
                    PATTERN = re.compile(regex)
                    for line in inputLines:
                        if not (bool(re.search(PATTERN, line)) or (re.match(PATTERN, line)) or (PATTERN == line) or (PATTERN in line)):
                            keptLines.append(line)
                    io = TEA_RunTime.NL.join(keptLines)
            return io


        def process_l(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "L":
                if len(tpe_str) == 0:
                    pass
                else:
                    lBlockName = tpe_str
                    # prevent duplication of block names
                    if not (lBlockName in LABELBLOCKS):
# store current code position under given label block name
# but most likely, has already been done during TSRC pre-processing/validation
                        LABELBLOCKS[lBlockName] = ATPI
            if tc == "L!":
                if len(tpe_str) == 0:
                    pass
                else:
                    labels = tpe_str.split(TEA_RunTime.TIPED)
                    for lBlockName in labels:
                        # prevent duplication of block names
                        if not (lBlockName in LABELBLOCKS):
                            LABELBLOCKS[lBlockName] = ATPI

            return io


        def process_m(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "M":
                input_str = tpe_str if len(tpe_str) > 0 else ai
                io = util_mirror_words(input_str)
            if tc == "M!":
                input_str = tpe_str if len(tpe_str) > 0 else ai
                io = util_mirror_chars(input_str)
            if tc == "M*":
                input_str = vault_get(tpe_str) if len(tpe_str) > 0 else ai
                io = util_mirror_words(input_str)
            if tc == "M*!":
                input_str = vault_get(tpe_str) if len(tpe_str) > 0 else ai
                io = util_mirror_chars(input_str)
            return io


        def process_n(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if (tc == "N") or (tc == "N!"):
                if len(tpe_str) == 0:
                    limit = 9
                    io = str(util_gen_rand(limit))
                else:
                   params  = tpe_str.split(TEA_RunTime.TIPED)
                   if len(params) == 1:
                       limit = params[0]
                       io = str(util_gen_rand(int(limit)))
                   if len(params) == 2:
                       limit,llimit = params
                       io = str(util_gen_rand(int(limit), ll=llimit))
                   if len(params) == 3:
                       limit,llimit,size = params
                       nums = []
                       for i in range(int(size)):
                           nums.append(str(util_gen_rand(int(limit), ll=llimit)))
                       io = TEA_RunTime.GLUE.join(nums)
                   if len(params) == 4:
                       limit,llimit,size,glue = params
                       nums = []
                       for i in range(int(size)):
                           nums.append(str(util_gen_rand(int(limit), ll=llimit)))
                       io = glue.join(nums)
            if (tc == "N*") or (tc == "N*!"):
                if len(tpe_str) == 0:
                    return io
                else:
                   params  = tpe_str.split(TEA_RunTime.TIPED)
                   if len(params) == 1:
                       vlimit = params[0]
                       limit = vault_get(vlimit) if len(vlimit) > 0 else 9
                       io = str(util_gen_rand(int(limit)))
                   if len(params) == 2:
                       limit,llimit = params

                       vlimit = limit
                       limit = vault_get(vlimit) if len(vlimit) > 0 else 9

                       vllimit = llimit
                       llimit = vault_get(vllimit) if len(vllimit) > 0 else 0

                       io = str(util_gen_rand(int(limit), ll=llimit))
                   if len(params) == 3:
                       limit,llimit,size = params

                       vlimit = limit
                       limit = vault_get(vlimit) if len(vlimit) > 0 else 9

                       vllimit = llimit
                       llimit = vault_get(vllimit) if len(vllimit) > 0 else 0

                       vsize = size
                       size = vault_get(vsize) if len(vsize) > 0 else 1

                       nums = []
                       for i in range(int(size)):
                           nums.append(str(util_gen_rand(int(limit), ll=llimit)))
                       io = TEA_RunTime.GLUE.join(nums)
                   if len(params) == 4:
                       limit,llimit,size,glue = params

                       vlimit = limit
                       limit = vault_get(vlimit) if len(vlimit) > 0 else 9

                       vllimit = llimit
                       llimit = vault_get(vllimit) if len(vllimit) > 0 else 0

                       vsize = size
                       size = vault_get(vsize) if len(vsize) > 0 else 1

                       vglue = size
                       glue = vault_get(vglue) if len(vglue) > 0 else TEA_RunTime.GLUE

                       nums = []
                       for i in range(int(size)):
                           nums.append(str(util_gen_rand(int(limit), ll=llimit)))
                       io = glue.join(nums)

            return io


        def process_o(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "O":
                input_str = tpe_str if len(tpe_str) > 0 else ai
                io = util_sort_words(input_str)
            if tc == "O!":
                input_str = tpe_str if len(tpe_str) > 0 else ai
                io = util_sort_chars(input_str)
            if tc == "O*":
                input_str = vault_get(tpe_str) if len(tpe_str) > 0 else ai
                io = util_sort_words(input_str)
            if tc == "O*!":
                input_str = vault_get(tpe_str) if len(tpe_str) > 0 else ai
                io = util_sort_chars(input_str)
            return io


        def process_p(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "P":
                if len(tpe_str) == 0:
                    io = util_gen_permutations(ai)
                else:
                    params = tpe_str.split(TEA_RunTime.TIPED)
                    if len(params) == 1:
                        io = util_gen_permutations(params[0])
                    elif len(params) == 2:
                        io = util_gen_permutations(params[0], glue=params[1])
                    elif len(params) == 3:
                        io = util_gen_permutations(params[0], glue=params[1], limit = int(params[2]))
                    else:
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} Invoked with Invalid Signature")
                        raise ValueError("[SEMANTIC ERROR] Invalid Instruction Signature")
            if tc == "P!":
                if len(tpe_str) == 0:
                    io = util_gen_rand_string()
                else:
                    params = tpe_str.split(TEA_RunTime.TIPED)
                    if len(params) == 1:
                        io = util_gen_rand_string(size=int(params[0]))
                    elif len(params) == 2:
                        io = util_gen_rand_string(size=int(params[0]), alphabet=params[1])
                    elif len(params) == 3:
                        io = util_gen_rand_string(size=int(params[0]), alphabet=params[1], glue = params[2])
                    else:
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} Invoked with Invalid Signature")
                        raise ValueError("[SEMANTIC ERROR] Invalid Instruction Signature")
            if tc == "P*":
                if len(tpe_str) == 0:
                    pass
                else:
                    params = tpe_str.split(TEA_RunTime.TIPED)
                    vNAME = params[0]
                    input_str = vault_get(vNAME)
                    if len(params) == 1:
                        io = util_gen_permutations(input_str)
                    elif len(params) == 2:
                        io = util_gen_permutations(input_str, glue=params[1])
                    elif len(params) == 3:
                        io = util_gen_permutations(input_str, glue=params[1], limit = int(params[2]))

            return io


        def process_q(ti, ai, _ATPI):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "Q":
                if len(tpe_str) == 0:
                    if (io is None) or (io == TEA_RunTime.EMPTY_STR):
                        if TEA_RunTime.DEBUG:
                            print(f"-- Quiting Program because AI is EMPTY")
                        _ATPI = len(INSTRUCTIONS) + 1 # points to end of program
                else:
                    qtest = tpe_str
                    if (bool(re.search(qtest, io)) or (re.match(qtest, io)) or (qtest == io) or (qtest in io)):
                        if TEA_RunTime.DEBUG:
                            print(f"Quiting Program because AI[{ai}] matches quit pattern[{qtest}]")
                        _ATPI = len(INSTRUCTIONS) + 1
            if tc == "Q!":
                if len(tpe_str) == 0:
                    if TEA_RunTime.DEBUG:
                        print(f"-- UNCONDITIONALLY Quiting Program")
                    _ATPI = len(INSTRUCTIONS) + 1
                    return io,_ATPI
                else:
                    qtest = tpe_str
                    if not (bool(re.search(qtest, io)) or (re.match(qtest, io)) or (qtest == io) or (qtest in io)):
                        if TEA_RunTime.DEBUG:
                            print(f"Quiting Program because AI[{ai}] does NOT match non-quit pattern[{qtest}]")
                        _ATPI = len(INSTRUCTIONS) + 1

            _ATPI += 1 #move to next instruction if we didn't quit
            return io,_ATPI


        def process_r(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if io is None or len(io) == 0:
                return io
            if tc == "R":
                if len(tpe_str) == 0:
                    io = util_braille_projection1(io)
                else:
                    params = tpe_str.split(TEA_RunTime.TIPED, maxsplit=1)
                    if len(params) != 2:
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} Invoked with Invalid Signature")
                        raise ValueError("[SEMANTIC ERROR] Invalid Instruction Signature")
                    else:
                        regex = params[0]
                        replacement = params[1]
                        io = re.sub(regex, replacement, io, count=1)
            if tc == "R!":
                if len(tpe_str) == 0:
                    io = util_braille_projection2(io)
                else:
                    params = tpe_str.split(TEA_RunTime.TIPED, maxsplit=1)
                    if len(params) != 2:
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} Invoked with Invalid Signature")
                        raise ValueError("[SEMANTIC ERROR] Invalid Instruction Signature")
                    else:
                        regex = params[0]
                        replacement = params[1]
                        io = re.sub(regex, replacement, io)

            if tc == "R*":
                if len(tpe_str) == 0:
                    pass
                else:
                    params = tpe_str.split(TEA_RunTime.TIPED, maxsplit=2)
                    if (len(params) == 2) or (len(params) > 3):
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} Invoked with Invalid Signature")
                        raise ValueError("[SEMANTIC ERROR] Invalid Instruction Signature")
                    else:
                        if len(params) == 1:
                            vault = params[0]
                            input_str = vault_get(vault)
                            io = util_braille_projection1(input_str)
                        else:
                            vault = params[0]
                            regex = params[1]
                            replacement = params[2]
                            input_str = vault_get(vault)
                            io = re.sub(regex, replacement, input_str, count=1)

            if tc == "R*!":
                if len(tpe_str) == 0:
                    pass
                else:
                    params = tpe_str.split(TEA_RunTime.TIPED, maxsplit=2)
                    if (len(params) == 2) or (len(params) > 3):
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} Invoked with Invalid Signature")
                        raise ValueError("[SEMANTIC ERROR] Invalid Instruction Signature")
                    else:
                        if len(params) == 1:
                            vault = params[0]
                            input_str = vault_get(vault)
                            io = util_braille_projection2(input_str)
                        else:
                            vault = params[0]
                            regex = params[1]
                            replacement = params[2]
                            input_str = vault_get(vault)
                            io = re.sub(regex, replacement, input_str)

            return io



        def process_s(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)
            salt = TEA_RunTime.SINGLE_SPACE_CHAR

            if tc == "S":
                if len(tpe_str) == 0:
                    if (io is None) or (len(io) == 0):
                        # can't salt without input
                        return io
                    else:
                        io = util_salt_string(io,salt)
                else:
                    if (io is None) or (len(io) == 0):
                        # can't salt without input
                        return io
                    else:
                        params = tpe_str.split(TEA_RunTime.TIPED, maxsplit=3)
                        if len(params) == 1:
                            salt = params[0]
                            io = util_salt_string(io,salt)
                        elif len(params) == 2:
                            salt = params[0]
                            i_limit = int(params[1])
                            io = util_salt_string(io,salt,injection_limit=i_limit)
                        elif len(params) == 3:
                            salt = params[0]
                            i_limit = int(params[1])
                            l_limit = int(params[2])
                            io = util_salt_string(io,salt,injection_limit=i_limit, llimit=l_limit)
            if tc == "S!":
                if len(tpe_str) == 0:
                    if (io is None) or (len(io) == 0):
                        # can't unsalt without input
                        return io
                    else:
                        io = util_unsalt_string(io)
                else:
                    if (io is None) or (len(io) == 0):
                        # can't unsalt without input
                        return io
                    else:
                        params = tpe_str.split(TEA_RunTime.TIPED, maxsplit=3)
                        if len(params) == 1:
                            salt_regex = params[0]
                            io = util_unsalt_string(io,salt_pattern=salt_regex)
                        elif len(params) == 2:
                            salt_regex = params[0]
                            d_limit = int(params[1])
                            io = util_unsalt_string(io,salt_pattern=salt_regex, deletion_limit=d_limit)
                        elif len(params) == 3:
                            salt_regex = params[0]
                            d_limit = int(params[1])
                            l_limit = int(params[2])
                            io = util_unsalt_string(io,salt_pattern=salt_regex, deletion_limit=d_limit, llimit=l_limit)

            if tc == "S*":
                if len(tpe_str) == 0:
                    pass
                else:
                    params = tpe_str.split(TEA_RunTime.TIPED, maxsplit=3)
                    vault = params[0]
                    input_str = vault_get(vault)
                    io = input_str

                    if (io is None) or (len(io) == 0):
                        # can't salt without input
                        return io
                    else:
                        if len(params) == 2:
                            salt = params[1]
                            io = util_salt_string(io,salt)
                        elif len(params) == 3:
                            salt = params[1]
                            i_limit = int(params[2])
                            io = util_salt_string(io,salt,injection_limit=i_limit)
                        elif len(params) == 4:
                            salt = params[1]
                            i_limit = int(params[2])
                            l_limit = int(params[3])
                            io = util_salt_string(io,salt,injection_limit=i_limit, llimit=l_limit)

            if tc == "S*!":
                if len(tpe_str) == 0:
                    pass
                else:
                    params = tpe_str.split(TEA_RunTime.TIPED, maxsplit=3)
                    vault = params[0]
                    input_str = vault_get(vault)
                    io = input_str

                    if (io is None) or (len(io) == 0):
                        # can't unsalt without input
                        return io
                    else:
                        params = tpe_str.split(TEA_RunTime.TIPED, maxsplit=3)
                        if len(params) == 2:
                            salt_regex = params[1]
                            io = util_unsalt_string(io,salt_pattern=salt_regex)
                        elif len(params) == 3:
                            salt_regex = params[1]
                            d_limit = int(params[2])
                            io = util_unsalt_string(io,salt_pattern=salt_regex, deletion_limit=d_limit)
                        elif len(params) == 4:
                            salt_regex = params[1]
                            d_limit = int(params[2])
                            l_limit = int(params[3])
                            io = util_unsalt_string(io,salt_pattern=salt_regex, deletion_limit=d_limit, llimit=l_limit)

            return io


        def process_t(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "T":
                if len(tpe_str) == 0:
                    if (io is None) or (len(io) == 0):
                        if TEA_RunTime.DEBUG:
                            print(f"[NOT]Processing {tc} on EMPTY AI [{io}]")
                        return io
                    else:
                        if TEA_RunTime.DEBUG:
                            print(f"Processing {tc} on AI=[{io}]")
                        return util_triangular_reduction(io)
                else:
                        input_str = tpe_str
                        if TEA_RunTime.DEBUG:
                            print(f"Processing {tc} on TPE[{io}]")
                        return util_triangular_reduction(input_str)
            if tc == "T!":
                if len(tpe_str) == 0:
                    if (io is None) or (len(io) == 0):
                        return io
                    else:
                        return util_rightmost_triangular_reduction(io)
                else:
                        input_str = tpe_str
                        return util_rightmost_triangular_reduction(input_str)
            if tc == "T*":
                if len(tpe_str) == 0:
                    pass
                else:
                    vault = tpe_str
                    input_str = vault_get(vault)
                    return util_triangular_reduction(input_str)

            if tc == "T*!":
                if len(tpe_str) == 0:
                    pass
                else:
                    vault = tpe_str
                    input_str = vault_get(vault)
                    return util_rightmost_triangular_reduction(input_str)

            return io


        def process_u(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "U":
                if len(tpe_str) == 0:
                    if (io is None) or (len(io) == 0):
                        if TEA_RunTime.DEBUG:
                            print(f"[NOT]Processing {tc} on EMPTY AI [{io}]")
                        return io
                    else:
                        if TEA_RunTime.DEBUG:
                            print(f"Processing {tc} on AI=[{io}]")
                        return util_unique_projection_words(io)
                else:
                        input_str = tpe_str
                        return util_unique_projection_words(input_str)
            if tc == "U!":
                if len(tpe_str) == 0:
                    if (io is None) or (len(io) == 0):
                        return io
                    else:
                        return util_unique_projection_chars(io)
                else:
                        input_str = tpe_str
                        return util_unique_projection_chars(input_str)
            if tc == "U*":
                if len(tpe_str) == 0:
                    pass
                else:
                    vault = tpe_str
                    input_str = vault_get(vault)
                    return util_unique_projection_words(input_str)

            if tc == "U*!":
                if len(tpe_str) == 0:
                    pass
                else:
                    vault = tpe_str
                    input_str = vault_get(vault)
                    return util_unique_projection_chars(input_str)

            return io


        def process_v(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "V":
                if len(tpe_str) == 0:
                    if (io is None) or (len(io) == 0):
                        vault_store(TEA_RunTime.vDEFAULT_VAULT,TEA_RunTime.EMPTY_STR)
                    else:
                        if TEA_RunTime.DEBUG:
                            print(f"Processing {tc} on AI=[{io}]")
                        vault_store(TEA_RunTime.vDEFAULT_VAULT,io)
                else:
                    input_str = tpe_str
                    params = input_str.split(TEA_RunTime.TIPED, maxsplit=1)
                    if len(params) > 2:
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} Invoked with Invalid Signature")
                        raise ValueError("[SEMANTIC ERROR] Invalid Instruction Signature")
                    else:
                        if len(params) == 2:
                            vNAME,vVALUE = params[0], extract_str(params[1])
                            vault_store(vNAME,vVALUE)
                        elif len(params) == 1:
                            vNAME,vVALUE = params[0], io
                            vault_store(vNAME,vVALUE)

            if tc == "V!":
                if len(tpe_str) == 0:
                    if TEA_RunTime.vDEFAULT_VAULT not in VAULTS:
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} trying to access DEFAULT VAULT before it is set!")
                        raise ValueError("[MEMORY ERROR] ATTEMPT to ACCESS unset DEFAULT VAULT")
                    vVALUE = vault_get(TEA_RunTime.vDEFAULT_VAULT)
                    if TEA_RunTime.DEBUG:
                        print(f"[INFO] Returning Length of string  in DEFAULT VAULT [{vVALUE}]")
                    return len(vVALUE)
                else:
                        input_str = tpe_str
                        if TEA_RunTime.DEBUG:
                            print(f"[INFO] Returning Length of string [{input_str}]")
                        return len(input_str)
            if tc == "V*":
                if len(tpe_str) == 0:
                    if TEA_RunTime.DEBUG:
                        print(f"[ERROR] Instruction {ti} Invoked with Invalid Signature")
                    raise ValueError("[SEMANTIC ERROR] Invalid Instruction Signature")
                else:
                        input_str = tpe_str
                        params = input_str.split(TEA_RunTime.TIPED, maxsplit=1)
                        if len(params) > 2:
                            if TEA_RunTime.DEBUG:
                                print(f"[ERROR] Instruction {ti} Invoked with Invalid Signature")
                            raise ValueError("[SEMANTIC ERROR] Invalid Instruction Signature")
                        else:
                            if len(params) == 2:
                                vNAME,vVALUE = params
                                vault_store(vNAME,vVALUE)
                            elif len(params) == 1:
                                vNAME,vVALUE = params[0], io
                                vault_store(vNAME,vVALUE)

            if tc == "V*!":
                if len(tpe_str) == 0:
                    if TEA_RunTime.vDEFAULT_VAULT not in VAULTS:
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} trying to access DEFAULT VAULT before it is set!")
                        raise ValueError("[MEMORY ERROR] ATTEMPT to ACCESS unset DEFAULT VAULT")
                    vVALUE = vault_get(TEA_RunTime.vDEFAULT_VAULT)
                    if TEA_RunTime.DEBUG:
                        print(f"[INFO] Returning Length of string  in DEFAULT VAULT [{vVALUE}]")
                    return len(vVALUE)
                else:
                    vNAME = tpe_str
                    vVALUE = vault_get(vNAME)
                    if TEA_RunTime.DEBUG:
                        print(f"[INFO] Returning Length of string  in VAULT[{vNAME} = [{vNAME}]]")
                    return len(vVALUE)

            return io



        def process_w(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "W":
                if len(tpe_str) == 0:
                    URL = io
                    webRESULT = util_web_get(URL)
                    return webRESULT if webRESULT is not None else TEA_RunTime.EMPTY_STR
                else:
                    URL = tpe_str
                    webRESULT = util_web_get(URL)
                    return webRESULT if webRESULT is not None else TEA_RunTime.EMPTY_STR

            if tc == "W!":
                if len(tpe_str) == 0:
                    URL = io
                    webRESULT = util_web_post(URL, data=None)
                    return webRESULT if webRESULT is not None else TEA_RunTime.EMPTY_STR
                else:
                    URL = tpe_str
                    webRESULT = util_web_post(URL, data=io)
                    return webRESULT if webRESULT is not None else TEA_RunTime.EMPTY_STR

            if tc == "W*":
                if len(tpe_str) == 0:
                    URL = io
                    data = VAULTS
                    webRESULT = util_web_get(URL, data=data)
                    return webRESULT if webRESULT is not None else TEA_RunTime.EMPTY_STR
                else:
                    URL = io
                    data = VAULTS

                    params = tpe_str.split(TEA_RunTime.TIPED)
                    if len(params) == 1:
                        URL = params[0]
                    else:
                        _vaultData = {}
                        for vNAME in params[:1]:
                            _vaultData[vNAME] = vault_get(vNAME)
                        data = _vaultData

                    webRESULT = util_web_get(URL, data=data)
                    return webRESULT if webRESULT is not None else TEA_RunTime.EMPTY_STR

            if tc == "W*!":
                if len(tpe_str) == 0:
                    URL = io
                    data = VAULTS
                    webRESULT = util_web_post(URL, data=data)
                    return webRESULT if webRESULT is not None else TEA_RunTime.EMPTY_STR
                else:
                    URL = io
                    data = VAULTS

                    params = tpe_str.split(TEA_RunTime.TIPED)
                    if len(params) == 1:
                        URL = params[0]
                    else:
                        _vaultData = {}
                        for vNAME in params[:1]:
                            _vaultData[vNAME] = vault_get(vNAME)
                        data = _vaultData

                    webRESULT = util_web_post(URL, data=io)
                    return webRESULT if webRESULT is not None else TEA_RunTime.EMPTY_STR

            return io



        def process_x(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "X":
                if len(tpe_str) == 0:
                    if (io is None) or (len(io) == 0):
                        if TEA_RunTime.DEBUG:
                            print(f"[NOT]Processing {tc} on EMPTY AI [{io}]")
                        return io
                    else:
                        if TEA_RunTime.DEBUG:
                            print(f"Processing {tc} on AI=[{io}]")
                        return io + io
                else:
                        prefix = tpe_str
                        return prefix + io
            if tc == "X!":
                if len(tpe_str) == 0:
                    if (io is None) or (len(io) == 0):
                        if TEA_RunTime.DEBUG:
                            print(f"[NOT]Processing {tc} on EMPTY AI [{io}]")
                        return io
                    else:
                        if TEA_RunTime.DEBUG:
                            print(f"Processing {tc} on AI=[{io}]")
                        return io[:(len(io)//2)]
                else:
                        suffix = tpe_str
                        return io + suffix

            if tc == "X*":
                if len(tpe_str) == 0:
                    pass
                else:
                    params = tpe_str.split(TEA_RunTime.TIPED, maxsplit=1)
                    val = io
                    if len(params) == 1:
                        vPREFIX = params[0]
                        prefix = vault_get(vPREFIX)
                        return prefix + val
                    if len(params) == 2:
                        vPREFIX = params[0]
                        vSTR = params[1]
                        prefix = vault_get(vPREFIX)
                        val = vault_get(vSTR)
                        return prefix + val

            if tc == "X*!":
                if len(tpe_str) == 0:
                    pass
                else:
                    params = tpe_str.split(TEA_RunTime.TIPED, maxsplit=1)
                    val = io
                    if len(params) == 1:
                        vSUFFIX = params[0]
                        suffix = vault_get(vSUFFIX)
                        return val + suffix
                    if len(params) == 2:
                        vSUFFIX = params[0]
                        vSTR = params[1]
                        suffix = vault_get(vSUFFIX)
                        val = vault_get(vSTR)
                        return val + suffix

            return io


        def process_y(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "Y":
                if len(tpe_str) == 0:
                    if TEA_RunTime.vDEFAULT_VAULT not in VAULTS:
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} trying to access DEFAULT VAULT before it is set!")
                        raise ValueError("[MEMORY ERROR] ATTEMPT to ACCESS unset DEFAULT VAULT")
                    vVALUE = vault_get(TEA_RunTime.vDEFAULT_VAULT)
                    if TEA_RunTime.DEBUG:
                        print(f"[INFO] Returning string in DEFAULT VAULT [{vVALUE}]")
                    return vVALUE
                else:
                    vNAME = tpe_str
                    vVALUE = vault_get(vNAME)
                    if TEA_RunTime.DEBUG:
                        print(f"[INFO] Returning string in VAULT [{vNAME}]")
                    return vVALUE
            if tc == "Y!":
                if len(tpe_str) == 0:
                    if TEA_RunTime.vDEFAULT_VAULT not in VAULTS:
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} trying to access DEFAULT VAULT before it is set!")
                        raise ValueError("[MEMORY ERROR] ATTEMPT to ACCESS unset DEFAULT VAULT")
                    vVALUE = vault_get(TEA_RunTime.vDEFAULT_VAULT)
                    if TEA_RunTime.DEBUG:
                        print(f"[INFO] Returning Length of string  in DEFAULT VAULT [{vVALUE}]")
                    return len(vVALUE)
                else:
                    vNAME = tpe_str
                    vVALUE = vault_get(vNAME)
                    if TEA_RunTime.DEBUG:
                        print(f"[INFO] Returning Length of string  in VAULT[{vNAME}]")
                    return len(vVALUE)

            if tc == "Y*":
                if len(tpe_str) == 0:
                    if TEA_RunTime.DEBUG:
                        print(f"[INFO] Returning ORIGINAL INPUT to the TEA PROGRAM")
                    return ORIGINAL_INPUT
                else:
                    vNAME = tpe_str
                    vVALUE = vault_get(vNAME)
                    if TEA_RunTime.DEBUG:
                        print(f"[INFO] Returning string in VAULT [{vNAME}]")
                    return vVALUE
            if tc == "Y*!":
                if len(tpe_str) == 0:
                    if TEA_RunTime.vDEFAULT_VAULT not in VAULTS:
                        if TEA_RunTime.DEBUG:
                            print(f"[ERROR] Instruction {ti} trying to access DEFAULT VAULT before it is set!")
                        raise ValueError("[MEMORY ERROR] ATTEMPT to ACCESS unset DEFAULT VAULT")
                    vVALUE = vault_get(TEA_RunTime.vDEFAULT_VAULT)
                    if TEA_RunTime.DEBUG:
                        print(f"[INFO] Returning Length of string  in DEFAULT VAULT [{vVALUE}]")
                    return len(vVALUE)
                else:
                    vNAME = tpe_str
                    vVALUE = vault_get(vNAME)
                    if TEA_RunTime.DEBUG:
                        print(f"[INFO] Returning Length of string  in VAULT[{vNAME}]")
                    return len(vVALUE)

            return io


        def process_z(ti, ai):
            io = ai if ai is not None else TEA_RunTime.EMPTY_STR
            tc, tpe = ti.split(TEA_RunTime.TCD, maxsplit=1)
            tc = tc.upper()
            tpe = tpe.strip()
            # extract the string parameter
            tpe_str = extract_str(tpe)

            if tc == "Z":
                if len(tpe_str) == 0:
                    return io.lower()
                else:
                    CMD = tpe_str
                    cmdDATA = io
                    cmdRESULT = util_system(CMD,cmdDATA)
                    return cmdRESULT if cmdRESULT is not None else TEA_RunTime.EMPTY_STR

            if tc == "Z!":
                if len(tpe_str) == 0:
                    return io.upper()
                else:
                    CMD = tpe_str
                    cmdDATA = io
                    cmdRESULT = util_system(CMD,cmdDATA, show_errors=True)
                    return cmdRESULT if cmdRESULT is not None else TEA_RunTime.EMPTY_STR

            if tc == "Z*":
                if len(tpe_str) == 0:
                    return io.title()
                else:
                    vCMD = tpe_str
                    CMD = vault_get(vCMD)
                    cmdDATA = io
                    cmdRESULT = util_system(CMD,cmdDATA)
                    return cmdRESULT if cmdRESULT is not None else TEA_RunTime.EMPTY_STR

            if tc == "Z*!":
                    vCMD = tpe_str
                    CMD = vault_get(vCMD)
                    cmdDATA = io
                    cmdRESULT = util_system(CMD,cmdDATA, show_errors=True)
                    return cmdRESULT if cmdRESULT is not None else TEA_RunTime.EMPTY_STR

            return io



#-----------------------------
# CLI Interface
#-----------------------------

# let us setup cli processing...
        if not _process_cli:
            INPUT = _ai # use input sent to the runtime...
        else:
            parser = argparse.ArgumentParser(
                                prog='tttt',
                                description='tttt is an interpreter for the TEA language',
                                epilog="""
            NOTE: tttt can also accept input from other processes via standard input such
            piping the output of other programs to tttt:
            <<

            echo INPUT | tttt

            >>
            In this case, with no other arguments to tttt, it is assumed INPUT is a TEA program
            (with or without in-code inputs), otherwise, if either -i or -fi are used in this mode
            such as with
            <<

            echo INPUT | tttt -i DATA

            >>
            <<

            echo INPUT | tttt -fi FDATA

            >>
            DATA or the text from FDATA take precendence as INPUT to tttt unless they are found to
            be blank or Null -- such as with a none-existent/inaccessible FDATA. Also, in these two
            cases, if no -c or -fc option was specified, then tttt assumed INPUT is the TEA program
            """)

            group_i = parser.add_mutually_exclusive_group()
            group_c = parser.add_mutually_exclusive_group()

            parser.add_argument("-d", "--debug", help="Turn debugging ON", action="store_true")

            group_i.add_argument("-i", "--input", type=str, help="use INPUT as input")
            group_i.add_argument("-fi", "--input-file", type=str, help="read input from INPUT_FILE")

            group_c.add_argument("-c", "--code", type=str, help="use CODE as TEA program")
            group_c.add_argument("-fc", "--code-file", type=str, help="read TEA program from CODE_FILE")

            args = parser.parse_args()

            TEA_RunTime.DEBUG = True if args.debug else False # allow user to toggle debugging

            if args.code:
                CODE = args.code
            elif args.code_file:
                if TEA_RunTime.DEBUG:
                    print(f"Reading CODE from: {args.code_file}")
                CODE = read_file(args.code_file)
            else:
                if HasSTDIN:
                    CODE = STDINPUT
                    STDIN_AS_CODE = True
                if TEA_RunTime.DEBUG:
                    print("Using INPUT as CODE")


            if args.input:
                INPUT = args.input
            elif args.input_file:
                if TEA_RunTime.DEBUG:
                    print(f"Reading INPUT from: {args.input_file}")
                INPUT = read_file(args.input_file)
            else:
                if not STDIN_AS_CODE:
                    INPUT = STDINPUT
                    if TEA_RunTime.DEBUG:
                        print("No explicit INPUT found, using STDIN!")
                else:
                    if TEA_RunTime.DEBUG:
                        print("No explicit INPUT found!")


            if TEA_RunTime.DEBUG:
                print(f"INPUT:{os.linesep} {INPUT}")

            if TEA_RunTime.DEBUG:
                if CODE is None:
                    print("No CODE found!")
                else:
                    print(f"CODE:{os.linesep} {CODE}")

#-----------------------------
# TEA Processing
#-----------------------------

        if TEA_RunTime.DEBUG:
            print(f"---------[ IN TEA RUNTIME ]\n")

        OUTPUT = None
        INSTRUCTIONS = []

        if CODE:
            INSTRUCTIONS = self._parse_tea_code(CODE)

            if len(INSTRUCTIONS) == 0:
                if TEA_RunTime.DEBUG:
                    print(f"NO TEA Instruction Lines Found!")
                    exit()
        else:
            if TEA_RunTime.DEBUG:
                print("NO TEA CODE FOUND")
            exit()

        # By default, we set AI to the EMPTY STRING is if it was None or not set
        INPUT = INPUT or self.EMPTY_STR
# we store original input just in case we might need it later in the TEA program : see Y*:
        ORIGINAL_INPUT = INPUT
        # by default, the input is the output if not touched..
        OUTPUT = INPUT



        LABELBLOCKS = self._parse_labelblocks(INSTRUCTIONS, initial_labelblocks={})


        while(True):
            # detect end of program and quit
            if ATPI >= len(INSTRUCTIONS):
                break

            if TEA_RunTime.DEBUG:
                print(f"Executing Instruction#{ATPI} (out of {len(INSTRUCTIONS)})")

            instruction = INSTRUCTIONS[ATPI]


            if TEA_RunTime.DEBUG:
                print(f"Processing Instruction: {instruction}")
                print(f"PRIOR MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")

            TC = instruction.upper()[0]

            # A: Anagrammatize
            if TC == "A":
                OUTPUT = str(process_a(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # B: Basify
            if TC == "B":
                OUTPUT = str(process_b(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # C: Clear
            if TC == "C":
                OUTPUT = str(process_c(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # D: Delete
            if TC == "D":
                OUTPUT = str(process_d(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # E: Evaluate
            if TC == "E":
                OUTPUT, ATPI, INSTRUCTIONS, LABELBLOCKS = process_e(instruction, OUTPUT, INSTRUCTIONS, ATPI, LABELBLOCKS )
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                #ATPI += 1 # e: updates ATPI directly...
                continue

            # F: Fork
            if TC == "F":
                OUTPUT,ATPI = process_f(instruction, OUTPUT,ATPI)
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                #ATPI += 1 # f: updates ATPI directly...
                continue

            # G: Glue
            if TC == "G":
                OUTPUT = str(process_g(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # H: Hew
            if TC == "H":
                OUTPUT = str(process_h(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # I: Input
            if TC == "I":
                OUTPUT = str(process_i(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # J: Jump
            if TC == "J":
                OUTPUT,ATPI = process_j(instruction, OUTPUT, ATPI)
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                #ATPI += 1 # j: updates ATPI directly...
                continue

            # K: Keep
            if TC == "K":
                OUTPUT = str(process_k(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # L: Label
            if TC == "L":
                OUTPUT = str(process_l(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # M: Mirror
            if TC == "M":
                OUTPUT = str(process_m(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # N: Number
            if TC == "N":
                OUTPUT = str(process_n(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # O: Order
            if TC == "O":
                OUTPUT = str(process_o(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # P: Permutate
            if TC == "P":
                OUTPUT = str(process_p(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # Q: Quit
            if TC == "Q":
                OUTPUT,ATPI = process_q(instruction, OUTPUT, ATPI)
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                #ATPI += 1 # q: updates ATPI directly...
                continue

            # R: Replace
            if TC == "R":
                OUTPUT = str(process_r(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # S: Salt
            if TC == "S":
                OUTPUT = str(process_s(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # T: Transform
            if TC == "T":
                OUTPUT = str(process_t(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # U: Uniqueify
            if TC == "U":
                OUTPUT = str(process_u(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # V: Vault
            if TC == "V":
                OUTPUT = str(process_v(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # W: Webify
            if TC == "W":
                OUTPUT = str(process_w(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # X: Xenograft
            if TC == "X":
                OUTPUT = str(process_x(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # Y: Yank
            if TC == "Y":
                OUTPUT = str(process_y(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue

            # Z: Zap
            if TC == "Z":
                OUTPUT = str(process_z(instruction, OUTPUT))
                if TEA_RunTime.DEBUG:
                    print(f"RESULTANT MEMORY STATE: (={OUTPUT}, VAULTS:{VAULTS})")
                ATPI += 1
                continue


        return OUTPUT if OUTPUT is not None else TEA_RunTime.EMPTY_STR # in TEA, None is the EMPTY_STR


if __name__ == "__main__":
    runtime = TEA_RunTime()
    program_output = runtime.run_tttt(_process_cli=True, _debug=DEBUG)
    #program_output = runtime.run_tttt(_process_cli=False, _tsrc="p!:", _ai="123", _debug=False)
    print(program_output)
