from reaper_python import *


class ReaperLooper:

    def __init__(self):
        self.project = 0  # active project
        self._armed_tracks = None

    @property
    def num_tracks(self):
        return RPR_GetNumTracks()

    @property
    def armed_tracks(self):
        armed_tracks = []
        for i in range(self.num_tracks):
            track = RPR_GetTrack(self.project, i)
            armed = bool(RPR_GetMediaTrackInfo_Value(track, 'I_RECARM'))
            if armed:
                armed_tracks.append(track)
        return armed_tracks

    @property
    def is_playing(self):
        return RPR_GetPlayState() & 1

    @property
    def is_recording(self):
        return RPR_GetPlayState() & 4

    def select_track(self, track):
        # 40297 Track: Unselect all tracks
        RPR_Main_OnCommand(40297, 0)        
        RPR_SetTrackSelected(track, True)

    def select_all_items_on_track(self, track):
        # 40289 Item: Unselect all items
        RPR_Main_OnCommand(40289, 0)
        self.select_track(track)
        # 40421 Item: Select all items in selected tracks
        RPR_Main_OnCommand(40421, 0)

    def get_last_item_on_track(self, track):
        self.select_all_items_on_track(track)        
        last_selected_item = RPR_CountSelectedMediaItems(self.project)
        if last_selected_item > 0:
            last_selected_item -= 1
        RPR_ShowConsoleMsg(last_selected_item)
        return RPR_GetSelectedMediaItem(self.project, last_selected_item)
        
    def duplicate_track(self, track):
        self.select_track(track)
        # 40062	Track -> Duplicate selected tracks
        RPR_Main_OnCommand(40062, 0)

        # New duplicated track is selected - this will be our clean, 'record' track.
        # Then lets clear all items off the 'record' track.
        # 40421 Item: Select all items in selected tracks
        RPR_Main_OnCommand(40421, 0)
        # 40006	Item: Remove selected items
        RPR_Main_OnCommand(40006, 0)
        
    def loop_items_on_track(self, track):
        item = self.get_last_item_on_track(track)
        RPR_ShowConsoleMsg(item)
        # RPR_SetMediaItemInfo_Value(item, 'I_CUSTOMCOLOR', RPR_ColorToNative(0, 220, 189)|0x01000000)
        RPR_SetMediaItemInfo_Value(item, 'B_LOOPSRC', True)
        RPR_SetMediaItemInfo_Value(item, 'D_LENGTH', 1000)

    def clear_track_sends(self, track, receive=False):
        idx = -1 if receive else 0
        send_count = RPR_GetTrackNumSends(track, idx)
        for i in range(send_count):
            RPR_ShowConsoleMsg("{} {}\n".format(RPR_RemoveTrackSend(track, idx, 0), i))

    def move_track_to_end(self, track):
        self.select_track(track)
        track_count = RPR_CountTracks(self.project)
        RPR_ReorderSelectedTracks(track_count, 0)
        
    def trigger(self):
        if self.is_recording:
            for track in self.armed_tracks:
                RPR_SetMediaTrackInfo_Value(
                    track,
                    'I_RECARM',
                    0
                )
                RPR_Main_OnCommand(1007, 0)  # Set to Play
                self.loop_items_on_track(track)
                self.duplicate_track(track)
                self.clear_track_sends(track)
                self.clear_track_sends(track, receive=True)
                self.move_track_to_end(track)
        else:
            RPR_Main_OnCommand(1013, 0)  # Set to Record

if __name__ == "__main__":
    looper = ReaperLooper()
    looper.trigger()
