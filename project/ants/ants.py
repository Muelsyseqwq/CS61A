"""Ants Vs. SomeBees."""

from __future__ import annotations  # This makes the type annotations work
import random
from ucb import main, interact, trace
from collections import OrderedDict

################
# Core Classes #
################


class Place:
    """A Place holds insects and has an exit to another Place."""
    is_hive = False

    def __init__(self, name: str, exit: Place | None = None):
        """Create a Place with the given NAME and EXIT.

        name -- A string; the name of this Place.
        exit -- The Place reached by exiting this Place (may be None).
        """
        self.name = name
        self.exit = exit
        self.bees: list[Bee] = []
        self.ant: Ant | None = None
        self.entrance: Place | None = None
        # Phase 1: Add an entrance to the exit
        # BEGIN Problem 2
        "*** YOUR CODE HERE ***"
        if exit: exit.entrance = self
        # END Problem 2

    def add_insect(self, insect: Insect):
        """Asks the insect to add itself to this place. This method exists so
        that it can be overridden in subclasses.
        """
        insect.add_to(self)

    def remove_insect(self, insect: Insect):
        """Asks the insect to remove itself from this place. This method exists so
        that it can be overridden in subclasses.
        """
        insect.remove_from(self)

    def __str__(self) -> str:
        return self.name


class Insect:
    """An Insect, the base class of Ant and Bee, has health and a Place."""

    next_id = 0  # Every insect gets a unique id number
    damage = 0
    is_waterproof = False
    # ADD CLASS ATTRIBUTES HERE

    def __init__(self, health: int, place: Place | None = None):
        """Create an Insect with a health and a starting PLACE."""
        self.health = health
        self.full_health = health
        self.place = place

        # assign a unique ID to every insect
        self.id = Insect.next_id
        Insect.next_id += 1

    def reduce_health(self, damage_taken: float):
        """Reduce health by DAMAGE_TAKEN, and remove the insect from its place if it
        has no health remaining. Decorated in gui.py for GUI support.

        >>> test_insect = Insect(5)
        >>> test_insect.reduce_health(2)
        >>> test_insect.health
        3
        """
        self.health -= damage_taken
        if self.health <= 0:
            self.zero_health_callback()

            if self.place is not None:
                self.place.remove_insect(self)

    def action(self, gamestate: GameState):
        """The action performed each turn."""

    def zero_health_callback(self):
        """
        Called when health reaches 0 or below.
        Decorated in gui.py to support GUI
        """

    def add_to(self, place: Place):
        self.place = place

    def remove_from(self, place: Place):
        self.place = None

    def __repr__(self):
        cname = type(self).__name__
        return '{0}({1}, {2})'.format(cname, self.health, self.place)


class Ant(Insect):
    """An Ant occupies a place and does work for the colony."""

    implemented = False  # Only implemented Ant classes should be instantiated
    food_cost = 0
    is_container = False
    blocks_path = True
    # ADD CLASS ATTRIBUTES HERE

    def __init__(self, health: int = 1):
        super().__init__(health)
        self.has_doubled = False
        self.ant_contained = None

    def can_contain(self, other: Ant) -> bool:
        return False

    def store_ant(self, ant: Ant):
        assert False, "{0} cannot contain an ant".format(self)

    def remove_ant(self, ant: Ant):
        assert False, "{0} cannot contain an ant".format(self)

    def add_to(self, place: Place):
        if place.ant is None:
            place.ant = self
        else:
            # BEGIN Problem 8b
            if place.ant.is_container and place.ant.can_contain(self): #if the ant in the place is the container
                place.ant.store_ant(self)

            elif self.is_container and self.can_contain(place.ant):
                self.store_ant(place.ant)
                place.ant = self
            else:
                assert ( self.is_container and self.can_contain(place.ant)) or (place.ant.is_container and place.ant.can_contain(self) ), 'Too many ants in {0}'.format(place)
            # END Problem 8b
        Insect.add_to(self, place)

    def remove_from(self, place: Place):
        if place.ant is self:
            place.ant = None
        elif place.ant is None:
            assert False, '{0} is not in {1}'.format(self, place)
        else:
            place.ant.remove_ant(self)
        Insect.remove_from(self, place)

    def double(self):
        """Double this ants's damage, if it has not already been doubled."""
        # BEGIN Problem 12
        "*** YOUR CODE HERE ***"
        if not self.has_doubled:
            self.has_doubled = True
            self.damage *= 2
        if self.is_container and self.ant_contained is not None:
            self.ant_contained.double()
                # END Problem 12



class HarvesterAnt(Ant):
    """HarvesterAnt produces 1 additional food per turn for the colony."""

    name = 'Harvester'
    implemented = True
    food_cost = 2
    # OVERRIDE CLASS ATTRIBUTES HERE

    def action(self, gamestate: GameState):
        """Produce 1 additional food for the colony.

        gamestate -- The GameState, used to access game state information.
        """
        # BEGIN Problem 1
        "*** YOUR CODE HERE ***"
        gamestate.food = gamestate.food + 1
        # END Problem 1


class ThrowerAnt(Ant):
    """ThrowerAnt throws a leaf each turn at the nearest Bee in its range."""

    name = 'Thrower'
    food_cost = 3
    implemented = True
    damage = 1
    lower_bound = 0
    upper_bound = float('inf')
    # ADD/OVERRIDE CLASS ATTRIBUTES HERE

    def nearest_bee(self) -> Bee | None:
        """Return a random Bee from the nearest Place (excluding the Hive) that contains Bees and is reachable from
        the ThrowerAnt's Place by following entrances.
D
        This method returns None if there is no such Bee (or none in range).
        """
        if not self.place:
            return None  # An Ant that is not in a Place has no nearest Bee
        # BEGIN Problem 3 and 4
        entr = self.place
        dist = 0
        while not entr.is_hive:
            # print(f"DEBUG:{entr.name}")
            if entr.bees and self.lower_bound <= dist <= self.upper_bound:
                # print(f"DEBUG:{entr.bees}")
                return random_bee(entr.bees) # REPLACE THIS LINE
            entr = entr.entrance
            dist += 1
            # print(f"DEBUG:{entr.name}")
        # END Problem 3 and 4
        return None

    def throw_at(self, target: Bee | None):
        """Throw a leaf at the target Bee, reducing its health."""
        if target is not None:
            target.reduce_health(self.damage)

    def action(self, gamestate: GameState):
        """Throw a leaf at the nearest Bee in range."""
        self.throw_at(self.nearest_bee())


def random_bee(bees: list[Bee]) -> Bee | None:
    """Return a random bee from a list of bees, or return None if bees is empty."""
    assert isinstance(bees, list), \
        "random_bee's argument should be a list but was a %s" % type(bees).__name__
    if bees:
        return random.choice(bees)

##############
# Extensions #
##############


class ShortThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at most 3 places away."""

    name = 'Short'
    food_cost = 2
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 4
    lower_bound = 0
    upper_bound = 3

    implemented = True   # Change to True to view in the GUI
    # END Problem 4


class LongThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at least 5 places away."""

    name = 'Long'
    food_cost = 2
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 4
    lower_bound = 5
    upper_bound = float('inf')

    implemented = True  # Change to True to view in the GUI
    # END Problem 4


class FireAnt(Ant):
    """FireAnt cooks any Bee in its Place when it expires."""

    name = 'Fire'
    damage = 3
    food_cost = 5
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 5
    implemented = True  # Change to True to view in the GUI
    # END Problem 5

    def __init__(self, health: int = 3):
        """Create an Ant with a HEALTH quantity."""
        super().__init__(health)

    def reduce_health(self, damage_taken: float):
        """Reduce health by DAMAGE_TAKEN, and remove the FireAnt from its place if it
        has no health remaining.

        Make sure to reduce the health of each bee in the current place, and apply
        the additional damage if the fire ant dies.
        """
        # BEGIN Problem 5
        "*** YOUR CODE HERE ***"
        p = self.place
        Ant.reduce_health(self, damage_taken)
        if self.health <= 0:
            if p.bees:
                for bee in p.bees[:]:
                    bee.reduce_health(damage_taken + self.damage)
        else:
            if p.bees:
                for bee in p.bees[:]:
                    bee.reduce_health(damage_taken)

        # END Problem 5

# BEGIN Problem 6
# The WallAnt class
class WallAnt(Ant):
    name = 'Wall'
    food_cost = 4
    implemented = True

    def __init__(self, health: int = 4):
        super().__init__(health)
# END Problem 6

# BEGIN Problem 7
# The HungryAnt Class
class HungryAnt(Ant):
    name = 'Hungry'
    implemented = True
    food_cost = 4
    chew_cooldown = 3
    def __init__(self, health: int = 1):
        super().__init__(health)
        self.cooldown = 0
    
    def action(self, gamestate: GameState):
        if self.cooldown > 0:
            self.cooldown -= 1
        else:
            if self.place.bees:
                bee = random_bee(self.place.bees)
                bee.reduce_health(bee.health)
                self.cooldown = self.chew_cooldown
    
        

# END Problem 7


class ContainerAnt(Ant):
    """
    ContainerAnt can share a space with other ants by containing them.
    """
    is_container = True

    def __init__(self, health: int):
        super().__init__(health)
        self.ant_contained = None

    def can_contain(self, other: Ant) -> bool:
        # BEGIN Problem 8a
        "*** YOUR CODE HERE ***"
        if self.ant_contained is None and other.is_container == False :
            return True
        else: return False

        # END Problem 8a

    def store_ant(self, ant: Ant):
        # BEGIN Problem 8a
        "*** YOUR CODE HERE ***"
        if self.can_contain(ant):
            self.ant_contained = ant
        # END Problem 8a

    def remove_ant(self, ant: Ant):
        if self.ant_contained is not ant:
            assert False, "{} does not contain {}".format(self, ant)
        self.ant_contained = None

    def remove_from(self, place: Place):
        # Special handling for container ants
        if place.ant is self:
            # Container was removed. Contained ant should remain in the game
            place.ant = self.ant_contained
            Insect.remove_from(self, place)
        else:
            # default to normal behavior
            Ant.remove_from(self, place)

    def action(self, gamestate: GameState):
        # BEGIN Problem 8a
        "*** YOUR CODE HERE ***"
        if self.ant_contained is not None:
            self.ant_contained.action(gamestate)
        # END Problem 8a


class ProtectorAnt(ContainerAnt):
    """ProtectorAnt provides protection to other Ants."""

    name = 'Protector'
    food_cost = 4
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 8c
    implemented = True
    def __init__(self,health: int = 2):
        super().__init__(health)
    # END Problem 8c

# BEGIN Problem 9
# The TankAnt class
class TankAnt(ContainerAnt):
    name = 'Tank'
    food_cost = 6
    implemented = True
    damage = 1

    def __init__(self,health: int = 2):
        super().__init__(health)

    def action(self, gamestate: GameState):
        ContainerAnt.action(self, gamestate)
        if self.place.bees:
            for bee in self.place.bees[:]:
                bee.reduce_health(self.damage)


# END Problem 9


class Water(Place):
    """Water is a place that can only hold waterproof insects."""

    def add_insect(self, insect: Insect):
        """Add an Insect to this place. If the insect is not waterproof, reduce
        its health to 0."""
        # BEGIN Problem 10
        "*** YOUR CODE HERE ***"
        Place.add_insect(self,insect)
        if not insect.is_waterproof :
            insect.reduce_health(insect.health)
        # END Problem 10

# BEGIN Problem 11
# The ScubaThrower class
class ScubaThrower(ThrowerAnt):
    name = 'Scuba'
    food_cost = 6
    is_waterproof = True
    implemented = True

# END Problem 11


class QueenAnt(ThrowerAnt):
    """QueenAnt boosts the damage of all ants behind her."""

    name = 'Queen'
    food_cost = 7
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 12
    implemented = True   # Change to True to view in the GUI
    # END Problem 12

    def action(self, gamestate: GameState):
        """A queen ant throws a leaf, but also doubles the damage of ants
        in her tunnel.
        """
        # BEGIN Problem 12
        "*** YOUR CODE HERE ***"
        ThrowerAnt.action(self, gamestate)
        pl = self.place.exit
        while pl is not None:
            if pl.ant is not None: pl.ant.double()
            pl = pl.exit
        # END Problem 12

    def reduce_health(self, damage_taken: float):
        """Reduce health by DAMAGE_TAKEN, and if the QueenAnt has no health
        remaining, signal the end of the game.
        """
        # BEGIN Problem 12
        "*** YOUR CODE HERE ***"
        ThrowerAnt.reduce_health(self, damage_taken)
        if self.health <= 0:
            ants_lose()
        # END Problem 12


################
# Extra Challenge #
################

class SlowThrower(ThrowerAnt):
    """ThrowerAnt that causes Slow on Bees."""

    name = 'Slow'
    food_cost = 6
    cause_slow = 5
    damage = 0
    # BEGIN Problem EC 1
    implemented = True   # Change to True to view in the GUI
    # END Problem EC 1

    def throw_at(self, target: Bee | None):
        # BEGIN Problem EC 1
        "*** YOUR CODE HERE ***"
        if target is not None:
            target.reduce_health(self.damage)
            target.slow_turn = 5

            def instance_action(gamestate: GameState):
                if target.slow_turn == 0 or gamestate.time % 2 == 0:
                    Bee.action(target, gamestate)
                if target.slow_turn > 0: target.slow_turn -= 1
            target.action = instance_action



        # END Problem EC 1


class ScaryThrower(ThrowerAnt):
    """ThrowerAnt that intimidates Bees, making them back away instead of advancing."""

    name = 'Scary'
    food_cost = 6
    # BEGIN Problem EC 2
    implemented = True  # Change to True to view in the GUI
    scare_turn = 2
    damage = 0
    # END Problem EC 2

    def throw_at(self, target: Bee | None):
        # BEGIN Problem EC 2
        "*** YOUR CODE HERE ***"
        if target is not None:
            target.reduce_health(self.damage)
            target.scare(self.scare_turn)

        # END Problem EC 2


class NinjaAnt(Ant):
    """NinjaAnt does not block the path and damages all bees in its place."""

    name = 'Ninja'
    damage = 1
    food_cost = 5
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem EC 3
    implemented = True  # Change to True to view in the GUI
    blocks_path = False
    # END Problem EC 3

    def action(self, gamestate: GameState):
        # BEGIN Problem EC 3
        "*** YOUR CODE HERE ***"
        # END Problem EC 3
        if self.place.bees:
            for bee in self.place.bees[:]:
                bee.reduce_health(self.damage)


class LaserAnt(ThrowerAnt):
    """ThrowerAnt that damages all Insects standing in its path."""

    name = 'Laser'
    food_cost = 10
    damage = 2
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem EC 4
    implemented = True   # Change to True to view in the GUI
    # END Problem EC 4

    def __init__(self, health: int = 1):
        super().__init__(health)
        self.insects_shot = 0

    def insects_in_front(self) -> dict[Bee, int]:
        # BEGIN Problem EC 4
        distance = 0
        dict = {}
        if self.place.ant.is_container:
            dict[self.place.ant] = distance
        if self.place.bees:
            for bee in self.place.bees[:]:
                dict[bee] = distance
        distance = 1
        p = self.place.entrance
        while not p.is_hive:
            if p.ant : dict[p.ant] = distance
            if p.ant and p.ant.is_container:
                dict[p.ant.ant_contained] = distance
            if p.bees:
                for bee in p.bees[:]:
                    dict[bee] = distance
            p = p.entrance
            distance += 1
        return dict
        # END Problem EC 4

    def calculate_damage(self, distance: int) -> float:
        # BEGIN Problem EC 4.
        damage =  self.damage - distance * 0.25 - self.insects_shot * 0.0625
        if damage <= 0: return 0
        else: return damage

        # END Problem EC 4

    def action(self, gamestate: GameState):
        insects_and_distances = self.insects_in_front()
        LaserAnt.play_sound_effect() # laser beam sound effect
        for insect, distance in insects_and_distances.items():
            damage = self.calculate_damage(distance)
            insect.reduce_health(damage)
            if damage:
                self.insects_shot += 1

    @classmethod
    def play_sound_effect(cls):
        """Play laser sound effect. Decorated in gui.py"""
        pass


########
# Bees #
########

class Bee(Insect):
    """A Bee moves from place to place, following exits and stinging ants."""

    name = 'Bee'
    damage = 1
    is_waterproof = True

    def sting(self, ant: Ant):
        """Attack an ANT, reducing its health by 1."""
        ant.reduce_health(self.damage)

    def move_to(self, place: Place):
        """Move from the Bee's current Place to a new PLACE."""
        if self.place is not None:
            self.place.remove_insect(self)

        if place is not None:
            place.add_insect(self)

    def blocked(self) -> bool:
        """Return True if this Bee cannot advance to the next Place."""
        # Special handling for NinjaAnt
        # BEGIN Problem EC 3
        return self.place is not None and self.place.ant is not None and self.place.ant.blocks_path
        # END Problem EC 3

    def action(self, gamestate: GameState):
        """A Bee's action stings the Ant that blocks its exit if it is blocked,
        or moves to the exit of its current place otherwise.

        gamestate -- The GameState, used to access game state information.
        """
        destination = None
        turns = getattr(self,'scare_turns',0)
        if turns > 0:
            if self.place:
                self.scare_turns -= 1
                if self.place.entrance and not self.place.entrance.is_hive:
                    destination = self.place.entrance
                else:
                    destination = self.place
        else:
            if self.place:
                destination = self.place.exit


        if self.blocked() and self.place and self.place.ant:
            self.sting(self.place.ant)
        elif self.health > 0 and destination is not None:
            self.move_to(destination)

    def add_to(self, place: Place):
        place.bees.append(self)
        super().add_to(place)

    def remove_from(self, place: Place):
        place.bees.remove(self)
        super().remove_from(place)

    def scare(self, length: int):
        """
        If this Bee has not been scared before, cause it to attempt to
        go backwards LENGTH times.
        """
        # BEGIN Problem EC 2
        "*** YOUR CODE HERE ***"
        if not getattr(self,'has_been_scared',False):
            self.has_been_scared = True
            self.scare_turns = length

        # END Problem EC 2


class Wasp(Bee):
    """Class of Bee that has higher damage."""
    name = 'Wasp'
    damage = 2


class Boss(Wasp):
    """The leader of the bees. Damage to the boss by any attack is capped.
    """
    name = 'Boss'
    damage_cap = 8

    def reduce_health(self, damage_taken: float):
        super().reduce_health(min(damage_taken, self.damage_cap))

    @classmethod
    def play_sound_effect(cls):
        "Play sound effect when boss arrives! Decorated in gui.py"
        pass


class Hive(Place):
    """The Place from which the Bees launch their assault.

    assault_plan -- An AssaultPlan; when & where bees enter the colony.
    """
    is_hive = True

    def __init__(self, assault_plan: AssaultPlan):
        self.name = 'Hive'
        self.assault_plan = assault_plan
        self.bees: list[Bee] = []
        for bee in assault_plan.all_bees():
            self.add_insect(bee)
        # The following attributes are always None for a Hive
        self.entrance: None = None
        self.ant: None = None
        self.exit: Place | None = None

    def strategy(self, gamestate: GameState):
        exits = [p for p in gamestate.places.values() if p.entrance is self]

        for bee in self.assault_plan.get(gamestate.time, []):
            if Boss in bee.__class__.__mro__:
                Boss.play_sound_effect()
                GameState.display_notification('Boss Bee is Here!')
            bee.move_to(random.choice(exits))
            gamestate.active_bees.append(bee)

###################
# Game Components #
###################

class GameState:
    """An ant collective that manages global game state and simulates time.

    Attributes:
    time -- elapsed time
    food -- the colony's available food total
    places -- A list of all places in the colony (including a Hive)
    bee_entrances -- A list of places that bees can enter
    """

    def __init__(self, beehive: Hive, ant_types: list, create_places, dimensions, food: int = 2):
        """Create an GameState for simulating a game.

        Arguments:
        beehive -- a Hive full of bees
        ant_types -- a list of ant classes
        create_places -- a function that creates the set of places
        dimensions -- a pair containing the dimensions of the game layout
        """
        self.time: int = 0
        self.food = food
        self.beehive = beehive
        self.ant_types = OrderedDict((a.name, a) for a in ant_types)
        self.dimensions = dimensions
        self.active_bees: list = []
        self.configure(beehive, create_places)

    def configure(self, beehive: Hive, create_places):
        """Configure the places in the colony."""
        self.base: AntHomeBase = AntHomeBase('Ant Home Base')
        self.places: OrderedDict = OrderedDict()
        self.bee_entrances: list = []

        def register_place(place: Place, is_bee_entrance: bool):
            self.places[place.name] = place
            if is_bee_entrance:
                place.entrance = beehive
                self.bee_entrances.append(place)
        register_place(self.beehive, False)
        create_places(self.base, register_place,
                      self.dimensions[0], self.dimensions[1])

    def ants_take_actions(self): # Ask ants to take actions
        for ant in self.ants:
            if ant.health > 0:
                ant.action(self)

    def bees_take_actions(self, num_bees: int) -> int: # Ask bees to take actions
        for bee in self.active_bees[:]:
            if bee.health > 0:
                bee.action(self)
            if bee.health <= 0:
                num_bees -= 1
                self.active_bees.remove(bee)
        if num_bees == 0: # Check if player won
            GameState.play_win_sound()
            raise AntsWinException()
        return num_bees

    def simulate(self):
        """Simulate an attack on the ant colony. This is called by the GUI to play the game."""
        num_bees = len(self.bees)
        try:
            while True:
                self.beehive.strategy(self) # Bees invade from hive
                yield None # After yielding, players have time to place ants
                self.ants_take_actions()
                self.time += 1
                yield None # After yielding, wait for throw leaf animation to play, then ask bees to take action
                num_bees = self.bees_take_actions(num_bees)
        except AntsWinException:
            print('All bees are vanquished. You win!')
            yield True
        except AntsLoseException:
            print('The bees reached homebase or the queen ant queen has perished. Please try again :(')
            yield False

    def deploy_ant(self, place_name: str, ant_type_name: str) -> Ant | None:
        """Place an ant if enough food is available.

        This method is called by the current strategy to deploy ants.
        """
        ant_type = self.ant_types[ant_type_name]
        if ant_type.food_cost > self.food:
            message = 'Not enough food!'
            print(message)
            GameState.display_notification(message)
        else:
            ant: Ant = ant_type()
            self.places[place_name].add_insect(ant)
            self.food -= ant.food_cost
            return ant

    def remove_ant(self, place_name: str):
        """Remove an Ant from the game."""
        place = self.places[place_name]
        if place.ant is not None:
            place.remove_insect(place.ant)

    @staticmethod
    def display_notification(message):
        """Display a notification! Decorated in gui.py for GUI support"""
        pass

    @classmethod
    def play_win_sound(cls):
        """Play the sound effect when ants win! Decorated in gui.py"""
        pass

    @property
    def ants(self):
        return [p.ant for p in self.places.values() if p.ant is not None]

    @property
    def bees(self):
        return [b for p in self.places.values() for b in p.bees]

    @property
    def insects(self):
        return self.ants + self.bees

    def __str__(self):
        status = ' (Food: {0}, Time: {1})'.format(self.food, self.time)
        return str([str(i) for i in self.ants + self.bees]) + status


class AntHomeBase(Place):
    """AntHomeBase at the end of the tunnel, where the queen normally resides."""

    def add_insect(self, insect):
        """Add an Insect to this Place.

        Can't actually add Ants to a AntHomeBase. However, if a Bee attempts to
        enter the AntHomeBase, a AntsLoseException is raised, signaling the end
        of a game.
        """
        assert isinstance(insect, Bee), 'Cannot add {0} to AntHomeBase'
        raise AntsLoseException()


def ants_win():
    """Signal that Ants win."""
    raise AntsWinException()


def ants_lose():
    """Signal that Ants lose."""
    raise AntsLoseException()


def ant_types() -> list:
    """Return a list of all implemented Ant classes."""
    all_ant_types: list = []
    new_types: list = [Ant]
    while new_types:
        new_types = [t for c in new_types for t in c.__subclasses__()]
        all_ant_types.extend(new_types)
    return [t for t in all_ant_types if t.implemented]


def bee_types() -> list:
    """Return a list of all implemented Bee classes."""
    all_bee_types: list = []
    new_types: list = [Bee]
    while new_types:
        new_types = [t for c in new_types for t in c.__subclasses__()]
        all_bee_types.extend(new_types)
    return all_bee_types


class GameOverException(Exception):
    """Base game over Exception."""
    pass


class AntsWinException(GameOverException):
    """Exception to signal that the ants win."""
    pass


class AntsLoseException(GameOverException):
    """Exception to signal that the ants lose."""
    pass


###########
# Layouts #
###########


def wet_layout(queen: AntHomeBase, register_place, tunnels: int = 3, length: int = 9, moat_frequency: int = 3):
    """Register a mix of wet and and dry places."""
    for tunnel in range(tunnels):
        exit = queen
        for step in range(length):
            if moat_frequency != 0 and (step + 1) % moat_frequency == 0:
                exit = Water('water_{0}_{1}'.format(tunnel, step), exit)
            else:
                exit = Place('tunnel_{0}_{1}'.format(tunnel, step), exit)
            register_place(exit, step == length - 1)


def dry_layout(queen: AntHomeBase, register_place, tunnels: int = 3, length: int = 9):
    """Register dry tunnels."""
    wet_layout(queen, register_place, tunnels, length, 0)


#################
# Assault Plans #
#################

class AssaultPlan(dict):
    """The Bees' plan of attack for the colony.  Attacks come in timed waves.

    An AssaultPlan is a dictionary from times (int) to waves (list of Bees).

    >>> AssaultPlan().add_wave(4, 2)
    {4: [Bee(3, None), Bee(3, None)]}
    """
    def add_wave(self, bee_type, bee_health: int, time: int, count: int) -> AssaultPlan:
        """Add a wave at time with count Bees that have the specified health."""
        bees = [bee_type(bee_health) for _ in range(count)]
        self.setdefault(time, []).extend(bees)
        return self

    def all_bees(self) -> list:
        """Place all Bees in the beehive and return the list of Bees."""
        return [bee for wave in self.values() for bee in wave]