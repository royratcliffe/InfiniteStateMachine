(* --- Interface --- *)
{attribute 'suppress_warning' := '0561'}
FUNCTION DepthOfState : INT
VAR_INPUT
	itfState : IState;
	iDepth : INT;
	itfStates : REFERENCE TO IStateArray;
END_VAR
VAR
END_VAR

(* --- Implementation --- *)
IF itfState = 0 THEN
	DepthOfState := 0;
ELSE
	DepthOfState := Topology(itfState, iDepth, itfStates);
END_IF
