(* --- Interface --- *)
METHOD PUBLIC GoTo
VAR
	itfState : IState;
	fbStateMachine : StateMachine;
	iDepth : INT := 0;
END_VAR

(* --- Implementation --- *)
fbStateMachine.Jump(itfState);
WHILE iDepth < Depth() AND iDepth < fbStateMachine.Depth() AND IsSameState(AtLevel(iDepth), fbStateMachine.AtLevel(iDepth)) DO
	iDepth := iDepth + 1;
END_WHILE
WHILE Depth() > iDepth DO
	Leave();
END_WHILE
WHILE fbStateMachine.Depth() > iDepth DO
	Enter(fbStateMachine.AtLevel(iDepth));
	iDepth := iDepth + 1;
END_WHILE
