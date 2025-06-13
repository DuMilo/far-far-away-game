import pgzrun
from pgzero.builtins import Actor, clock

def build_tile_map(csv_path, tile_size, scale=1.0):
    try:
        with open(csv_path, "r") as f:
            map_data = f.read().splitlines()
    except FileNotFoundError:
        print(f"ERRO: Arquivo de mapa não encontrado em '{csv_path}'")
        return []

    tile_grid = [[int(col) for col in row.split(",")] for row in map_data]

    tile_actors = []
    for row_index, row in enumerate(tile_grid):
        for col_index, tile_gid in enumerate(row):
            if tile_gid == -1:
                continue

            flipped_h = bool(tile_gid & 0x80000000)
            flipped_v = bool(tile_gid & 0x40000000)
            
            tile_id = tile_gid & 0x0FFFFFFF

            image_name = f"tiles/tile_{tile_id:04d}"
            
            try:
                tile_actor = Actor(image_name)
            except FileNotFoundError:
                print(f"AVISO: Imagem '{image_name}.png' não encontrada. Ignorando tile.")
                continue

            tile_actor.width = tile_size * scale
            tile_actor.height = tile_size * scale
            
            if flipped_h:
                tile_actor.flip_x = True
            if flipped_v:
                tile_actor.flip_y = True

            tile_actor.topleft = (
                col_index * tile_size * scale,
                row_index * tile_size * scale
            )
            tile_actors.append(tile_actor)

    return tile_actors

class AnimatedActor(Actor):
    def __init__(self, image_prefix, frame_count, fps, **kwargs):
        self.image_prefix = image_prefix
        self.frame_count = frame_count
        self.fps = fps
        self.current_frame = 0
        self.is_paused = False

        self.images = [f"{image_prefix}{i}" for i in range(frame_count)]
        
        super().__init__(self.images[0], **kwargs)

        clock.schedule_interval(self.animate, 1.0 / self.fps)

    def animate(self):
        if not self.is_paused:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.image = self.images[self.current_frame]

    def pause_animation(self):
        self.is_paused = True

    def resume_animation(self):
        self.is_paused = False
        
    @property
    def flip_x(self):
        return self._flip_x

    @flip_x.setter
    def flip_x(self, value):
        self._flip_x = value
        self._transform_surf()

    @property
    def flip_y(self):
        return self._flip_y

    @flip_y.setter
    def flip_y(self, value):
        self._flip_y = value
        self._transform_surf()