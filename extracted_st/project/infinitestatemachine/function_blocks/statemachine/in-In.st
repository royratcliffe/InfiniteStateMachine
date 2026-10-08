(* --- Interface --- *)
METHOD In : BOOL
VAR_INPUT
	itfState: IState;
END_VAR
VAR
	iLevel : INT := 0;
END_VAR

(* --- Implementation --- *)
(*
 * The following do-while loop's condition assumes early-out semantics.
 * It assumes that the second sub-condition does *not* evaluate unless the first sub-condition is true.
 *)
WHILE iLevel < iDepth AND itfStates[iLevel] <> itfState DO
	iLevel := iLevel + 1;
END_WHILE
In := iLevel < iDepth;
