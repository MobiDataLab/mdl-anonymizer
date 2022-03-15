import logging
import random
import numpy as np
from tqdm import tqdm

from src.entities.Dataset import Dataset
from src.entities.Trajectory import Trajectory
from src.entities.TimestampedLocation import TimestampedLocation


class SwapMob:
	def __init__(self, dataset: Dataset, spatial_thold, temporal_thold):
		self.dataset = dataset
		self.spatial_thold = spatial_thold
		self.temporal_thold = temporal_thold

		self.anonymized_dataset = dataset.__class__()

	def run(self):	# TODO: Use to_numpy and from_numpy methods and adapt class methods to them
		# Create anonymized dataset as a copy of the original dataset
		for t in self.dataset.trajectories:
			self.anonymized_dataset.add_trajectory(Trajectory(t.id))    # TODO: Since I change trajectories, this must be an object copy
		logging.info("Anonymized dataset initialized!")

		# Get first and last timestamp of the dataset
		first_timestamp, last_timestamp = self.get_first_last_timestamp()

		# Swap trajectories
		logging.info("Swapping...")
		num_intervals = (last_timestamp - first_timestamp - 1) // self.temporal_thold + 1
		for i in tqdm(range(num_intervals), desc="Num. time intervals"):
			# Get initial and final timestamps of the interval
			ini_t = first_timestamp + i * self.temporal_thold
			end_t = min(ini_t + self.temporal_thold, last_timestamp)

			# Get locations in the interval
			traj_loc_pairs = self.get_locations_in_interval(ini_t, end_t)

			# Get possible swaps depending on the distance
			possible_swaps = self.get_possible_swaps(traj_loc_pairs)

			# TODO: Get selection of swaps

			# TODO: Perform swaps

		logging.info("Swapping done!")

		# Remove trajectories with less than 1 locations
		logging.info("Remove trajectories with less than 1 locations")
		self.anonymized_dataset.trajectories = [t for t in self.anonymized_dataset.trajectories if len(t) > 1]

		# Remove trajectories without swaps
		logging.info("Remove trajectories without swaps")
		# self.anonymized_dataset.trajectories = [t for t in self.anonymized_dataset.trajectories if len(t) > 1]  # TODO

		logging.info("Done!")

	def get_first_last_timestamp(self):
		first_timestamp = float("inf")
		last_timestamp = float("-inf")
		for t in self.anonymized_dataset.trajectories:
			if t.get_first_timestamp() < first_timestamp:
				first_timestamp = t.get_first_timestamp()
			if t.get_last_timestamp() > last_timestamp:
				last_timestamp = t.get_last_timestamp()

		return first_timestamp, last_timestamp

	def get_locations_in_interval(self, ini_t: float, end_t: float):
		traj_loc_pairs = []
		for traj in self.anonymized_dataset.trajectories:
			if traj.get_first_timestamp() <= ini_t < traj.get_last_timestamp():  # TODO: Check this
				for loc in traj.locations:
					if ini_t <= loc.timestamp <= end_t:
						traj_loc_pairs.append((traj, loc))

		return traj_loc_pairs

	def get_possible_swaps(self, traj_loc_pairs):
		possible_swaps = []
		for idx1, (t1, l1) in enumerate(traj_loc_pairs):
			if idx1 < len(traj_loc_pairs) - 1:
				for (t2, l2) in traj_loc_pairs[idx1 + 1:]:
					if l1.spatial_distance(l2) < self.spatial_thold:
						possible_swaps.append(((t1, l1), (t2, l2)))

		return possible_swaps

	def swap(self, t1: Trajectory, l1: TimestampedLocation, t2: Trajectory, l2: TimestampedLocation):
		return NotImplemented  # TODO

	def get_anonymized_dataset(self):
		return self.anonymized_dataset
