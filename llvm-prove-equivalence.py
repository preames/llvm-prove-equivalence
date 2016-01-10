#! /usr/bin/python
# Determine if the two input IR files can be proven to be semantically
# equivalent (modulo undefined behavior).  A common use case is to determine
# if IR from two different versions of the same program are semantically 
# equivalent.  This tool is unlikely to recognize two different implementations
# of an algorithm as semantically identical unless the implementations are
# overwhelming similiar in structure.  This could potentially be improved if
# motivating use cases were found.  Note that if one or both files include 
# execution paths which include undefined behavior, the results are undefined.

import os
import subprocess
import sys
import optparse


parser = optparse.OptionParser()
parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="Be verbose about differences in the input files")
(options, args) = parser.parse_args()

assert len(args) == 2
file1 = args[0]
file2 = args[1]
assert os.path.exists(file1)
assert os.path.exists(file2)

# TODO: early exit checks
# - If the inputs are the same, OK!

# Canonicalize inputs to remove source sensativities
# - debug info - Otherwise small line changes would cause differences in
#     both optimization and output.  Note that this is slightly risky since
#     the absence of debug info may enable optimizations not enabled in the
#     original build.  This is unlikely to mask problems unless it exposes
#     undefined behavior that a compile with debug info couldn't exploit.
# TODO:
# - module names?
# Note: When adding passes here, need to be careful not to remove 
# optimization hints.  Doing so would limit how well we can canonicalize
canonicalization_passes = " ".join(["-strip-debug", "-strip"])

cmd = "$LLVM_BASE_DIR/bin/opt %s -O3 %s" % (canonicalization_passes, file1)
output1 = subprocess.check_output(cmd, shell=True)

cmd = "$LLVM_BASE_DIR/bin/opt %s -O3 %s" % (canonicalization_passes, file2)
output2 = subprocess.check_output(cmd, shell=True)

if output1 == output2:
    print "Versions are semantically identical"
else:
    # TODO: Is it worth reporting cases which are obviously *NOT* the
    # same?  i.e. to prune more expensive searches?
    print "Versions are potentially different"
    if options.verbose:
        print ""
        print "Differences remaining (verbose):"
        # As a verbose debugging mode, use llvm-diff to try to understand 
        # the differences
        cmd = "$LLVM_BASE_DIR/bin/llvm-diff %s %s" % (file1, file2)
        try:
            output2 = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError:
            # purposely ignore error, the output got printed anyway
            pass
    sys.exit(1)

# Note: A more complicated scheme is possible, but the optimizer does a rather 
# good job of canonicalizing near by inputs to the same output on its own.  
# For instance, the optimizer will inline a single callee internal function 
# at nearly any cost.  This goes a long way to caonicalizing the before and 
# after image of a source level transformation like function outlining to the 
# same final IR.  The only major cases left are pass ordering problems, or 
# small changes which cause the optimizer to canonicalize radically 
# differently.  Given these are often compile bugs, it's not clear how much 
# work is worth investigating in proving them away vs fixing said bugs.

# OPTION 1
# 1 - Rename symbols in each
# 2 - link modules
# 3 - construct proof functions (e.g. see test-by-hand.ll)
# 4 - optimize functions
# $LLVM_BASE_DIR/bin/opt -always-inline -barrier -O3 -S test.ll
# 5 - check for use of first argument (%version)

# longer term, how deal with recursive constructs?

# OPTION 2
# merge functions

# OPTION 3
# - pose an SMT proof, but what does this get you in practice?  Complex NFC 
# changes aren't that common are they?
