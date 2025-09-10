

class GraphicalItem():
    def __init__(self):
        pass

    def draw(self, canvas, camera):
        """Draw the item on the canvas"""
        canvas.create_rectangle(camera.convert4D(50, 50, 200, 150), fill="blue", outline="black", width=2)