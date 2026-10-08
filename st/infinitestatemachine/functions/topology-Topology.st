(* --- Interface --- *)
{attribute 'suppress_warning' := '0561'}
FUNCTION Topology : INT
VAR_INPUT
	itfState : IState;
	iDepth : INT;
	itfStates : REFERENCE TO IStateArray;
END_VAR
VAR
END_VAR

(* --- Implementation --- *)
IF iDepth = 0 THEN
	Topology := 0;
ELSE
	Topology := DepthOfState(itfState.SuperState, iDepth - 1, itfStates);
	itfStates[Topology] := itfState;
	Topology := Topology + 1;
END_IF
