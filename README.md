llvm-prove-equivalence is a simple tool to determine if the two input IR files can be proven to be semantically equivalent (modulo undefined behavior).  A common use case is to determine if IR from two different versions of the same program are semantically  equivalent.  This tool is unlikely to recognize two different implementations of an algorithm as semantically identical unless the implementations are overwhelming similiar in structure.  This could potentially be improved if motivating use cases were found.  Note that if one or both files include execution paths which include undefined behavior, the results are undefined.

```
llvm-prove-equivalence.py version-a.ll version-b.ll
```

To use, you must have defined LLVM_BASE_DIR pointing a build or install directory of an LLVM checkout.
