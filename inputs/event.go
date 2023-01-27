package inputs

// Vector is for mapping from validatorId to highest observed event id
type Vector struct {
	eventId EventId
	seq     Seq
	isFork  bool
}

func (v *Vector) EventId() EventId { return v.eventId }
func (v *Vector) Seq() Seq         { return v.seq }
func (v *Vector) IsFork() bool     { return v.isFork }

func (v *Vector) SetEventId(s EventId) { v.eventId = s }
func (v *Vector) SetSeq(s Seq)         { v.seq = s }
func (v *Vector) SetIsFork(f bool)     { v.isFork = f }

// Events map[EventID]BaseEvent
type Events map[EventId]Event

type Event struct {
	// epoch number (see epoch). Not less than 1.
	epoch Epoch
	// seq number. Equal to self-parent’s seq + 1, if no self-parent, then 1.
	seq Seq
	// frame number (see consensus). Not less than 1.
	frame Frame
	// creator ID of validator which created event.
	creator ValidatorId
	// node owner of the event
	node NodeId
	// hash of the event
	id EventId
	// list of parents (graph edges). May be empty. If Seq > 1, then ﬁrst element is self-parent.
	parents Parents

	// mapping from validatorId to highest observed event id
	highestEventsVector map[ValidatorId]Vector
	// flag for root
	isRoot bool
}

func (e *Event) Epoch() Epoch                                { return e.epoch }
func (e *Event) Seq() Seq                                    { return e.seq }
func (e *Event) Frame() Frame                                { return e.frame }
func (e *Event) Creator() ValidatorId                        { return e.creator }
func (e *Event) Node() NodeId                                { return e.node }
func (e *Event) Id() EventId                                 { return e.id }
func (e *Event) Parents() Parents                            { return e.parents }
func (e *Event) IsRoot() bool                                { return e.isRoot }
func (e *Event) HighestEventsVector() map[ValidatorId]Vector { return e.highestEventsVector }

func (e *Event) SetEpoch(ep Epoch)        { e.epoch = ep }
func (e *Event) SetSeq(s Seq)             { e.seq = s }
func (e *Event) SetFrame(f Frame)         { e.frame = f }
func (e *Event) SetCreator(c ValidatorId) { e.creator = c }
func (e *Event) SetNode(n NodeId)         { e.node = n }
func (e *Event) SetId(i EventId)          { e.id = i }
func (e *Event) SetParents(p Parents)     { e.parents = p }

// SetEvent when adding a new event into dag
func (e *Event) SetEvent(events Events) {
	e.SetHighestEventsVector(events)
}

// SelfParent returns event's self-parent, if any
func (e *Event) SelfParent() *EventId {
	if e.seq <= 1 || len(e.parents) == 0 {
		return nil
	}
	return &e.parents[0]
}

// SetHighestEventsVector finds the highest events and detects whether there is a fork
func (e *Event) SetHighestEventsVector(events Events) {
	var vector Vector
	e.highestEventsVector = make(map[ValidatorId]Vector)
	// find the highest events
	// root
	if e.seq == 1 || events == nil {
		vector.SetEventId(e.id)
		vector.SetSeq(e.seq)
		e.highestEventsVector[e.creator] = vector
		for k, v := range events {
			for _, r := range e.parents {
				if k == r {
					vector.SetEventId(v.id)
					vector.SetSeq(v.seq)
					e.highestEventsVector[v.creator] = vector
				}
			}
		}
	} else {
		for k, v := range events {
			for _, r := range e.parents {
				// find the parent
				if k == r {
					var vector Vector
					vector.SetEventId(k)
					vector.SetSeq(v.Seq())
					e.highestEventsVector[v.creator] = vector
					// highest events observed by parents
					for i, j := range v.highestEventsVector {
						var ei Vector
						ei = e.highestEventsVector[i]
						if j.Seq() > ei.Seq() {
							ei.SetEventId(j.EventId())
							ei.SetSeq(j.Seq())
							e.highestEventsVector[i] = ei
						}
					}

				}
			}
		}
	}

	// Flag: if there is already present a different event with the same seq and epoch from the same validator
	for _, v := range events {
		if e.id != v.Id() && e.creator == v.Creator() && e.seq == v.Seq() && e.epoch == v.Epoch() {
			var v2 Vector
			v2 = e.highestEventsVector[e.creator]
			v2.SetIsFork(true)
			e.highestEventsVector[e.creator] = v2
		}
	}
	// This flag is then inherited for the given validator by parent events.
	for k, v := range events {
		for _, r := range e.parents {
			// find the parent
			if k == r {
				if v.highestEventsVector[v.creator].isFork {
					v2 := e.highestEventsVector[v.creator]
					v2.SetIsFork(true)
					e.highestEventsVector[v.creator] = v2
				}
			}
		}
	}
}

func (e *Event) SetRoot() {
	// The first event of a validator is a root.
	if e.Seq() == 1 {
		e.isRoot = true
	} else {
		// An event, which is forkless caused by the previous frame roots quorum is a root.

	}

}
