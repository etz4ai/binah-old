from pytube import Playlist, YouTube as PyYouTube
from binah.util import get_data_home
from binah.model import Video, Example, Type, Lifecycle, License, Dataset
import os

PLAYLISTS = ['https://www.youtube.com/watch?v=-yOPQN19c98&list=PL9uNqONsJ8Q9hmgft3ZsDiObSAaoJG6e0']
VIDEO_DIR = get_data_home() / 'videos'
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

def _create_or_use_youtube_license(session):
    query = session.query(License.id, License.name).filter(License.name == 'YouTube EULA').first()
    if query:
        lic_id = query.id
    else:
        row = License(name='YouTube EULA', url='https://www.youtube.com/static?template=terms')
        session.add(row)
        session.flush()
        lic_id = row.id
    return lic_id

def _create_or_use_youtube_dataset(session):
    query = session.query(Dataset.id, Dataset.name).filter(Dataset.name == 'YouTube').first()
    if query:
        dataset_id = query.id
    else:
        row = Dataset(name='YouTube', 
            desc="The world's most popular video sharing website.",
            url='https://www.youtube.com/')
        session.add(row)
        session.flush()
        dataset_id = row.id
    return dataset_id

def YouTube(session):
    lic_id = _create_or_use_youtube_license(session)
    dataset_id = _create_or_use_youtube_dataset(session)
    for playlist_uri in PLAYLISTS:
        playlist = Playlist(playlist_uri)
        playlist.populate_video_urls()
        for video_uri in playlist.video_urls:
            video = PyYouTube(video_uri)
            example = Example(dataset_id=dataset_id,
                        type=Type.MP4,
                        lifecycle=Lifecycle.FLEXIBLE,
                        license_id=lic_id
                        )
            session.add(example)
            session.flush()
            video.streams.filter(file_extension='mp4', only_video=True) \
                .order_by('resolution').desc().first() \
                .download(output_path=str(VIDEO_DIR), filename=str(example.id))
            video = Video(id=example.id, orig_url=video_uri)   
            session.add(video)
    session.commit()
