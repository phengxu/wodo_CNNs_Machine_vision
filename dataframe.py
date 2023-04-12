# draw a statistic graph on main screen
import config
import numpy as np
import itertools

class Dataframe():
    def __init__(self, cb):
        self.cb_draw_graph_prob = cb # wodo func draw graph file
        # each camera's dataframe data
        self.countprodnum_a = 0 #
        self.total_prob_list_a = []
        self.dataframe_a = []
        self.dataframe_a.append(list(range(config.TARGET_SIZE))) # 0 row as fixed x aix data for 1~30 targets
        da = {"framedata": self.dataframe_a, "count": self.countprodnum_a, "problist": self.total_prob_list_a}
        self.add_prediction_to_dataframe_a = self.make_data_frame(da)
        
        self.countprodnum_b = 0
        self.total_prob_list_b = []
        self.dataframe_b = []
        self.dataframe_b.append(list(range(config.TARGET_SIZE)))
        db = {"framedata": self.dataframe_b, "count": self.countprodnum_b, "problist": self.total_prob_list_b}
        self.add_prediction_to_dataframe_b = self.make_data_frame(db)
        
        self.countprodnum_c = 0
        self.total_prob_list_c = []
        self.dataframe_c = []
        self.dataframe_c.append(list(range(config.TARGET_SIZE)))
        dc = {"framedata": self.dataframe_c, "count": self.countprodnum_c, "problist": self.total_prob_list_c}
        self.add_prediction_to_dataframe_c = self.make_data_frame(dc)
            
        self.countprodnum_d = 0
        self.total_prob_list_d = []
        self.dataframe_d = []
        self.dataframe_d.append(list(range(config.TARGET_SIZE)))
        dd = {"framedata": self.dataframe_d, "count": self.countprodnum_d, "problist": self.total_prob_list_d}
        self.add_prediction_to_dataframe_d = self.make_data_frame(dd)
    # closure func for dataframe initing..........
    def make_data_frame(self, data):#dataframe, count, total_prob_list):
        def add_data_of_predictions(predictions, cam_id, batch_id):
            # add prediction to dataframe
            
            if config.CUTOFF_INDEX >0: # there are cutoff invalid prob
                # if current batch id is last batch, in this batch, there are invalid prob need to be cutoff
                if batch_id == (config.TARGET_SIZE//config.BATCH_SIZE) +1: # move to the last batch
                    # cutoff invalid prob
                    valid_probs = self.flt(predictions)[:config.BATCH_SIZE-config.CUTOFF_INDEX]
                    data["problist"].append(valid_probs)
                    # counter offset cutoff value
                    data["count"] += config.BATCH_SIZE - config.CUTOFF_INDEX
                else:
                    data["count"] += config.BATCH_SIZE
                    data["problist"].append(self.flt(predictions))
            else: # no cutoff in predictions
                data["count"] += config.BATCH_SIZE # each predict create 5 prob
                # get one batch results
                data["problist"].append(self.flt(predictions))
            if data["count"] % config.TARGET_SIZE == 0: # get all prob data from one piece
                one_piece_prob_list = [item for sublist in data["problist"] for item in sublist]
                data["problist"] = [] # clear batch content for next fill
                data["framedata"].append(one_piece_prob_list)
        return add_data_of_predictions
    # main func for worker
    def make_graph_data(self, predictions, cam_id, batch_id):
        # draw statistic graph to screen
        if cam_id == 0: # equal to camera a position topview
            # self.makedataframe_a(predictions,cb_draw_graph_prob, cam_id, batch_id)
            # if cam_mode == 'pm' or cam_mode == 'p': # if there are prediction operation
            self.add_prediction_to_dataframe_a(predictions, cam_id, batch_id)
            self.cb_draw_graph_prob(self.dataframe_a, cam_id) 
        if cam_id == 1: # equal to camera a position side front view
            # self.makedataframe_b(predictions,cb_draw_graph_prob, cam_id, batch_id)
            # if cam_mode == 'pm' or cam_mode == 'p':
            self.add_prediction_to_dataframe_b(predictions, cam_id, batch_id)
            self.cb_draw_graph_prob(self.dataframe_b, cam_id)
        if cam_id == 2:
            # self.makedataframe_c(predictions,cb_draw_graph_prob, cam_id, batch_id)
            # if cam_mode == 'pm' or cam_mode == 'p':
            self.add_prediction_to_dataframe_c(predictions, cam_id, batch_id)
            self.cb_draw_graph_prob(self.dataframe_c, cam_id)
        if cam_id == 3: # equal to camera a position
            # self.makedataframe_d(predictions,cb_draw_graph_prob, cam_id, batch_id)
            # if cam_mode == 'pm' or cam_mode == 'p':
            self.add_prediction_to_dataframe_d(predictions, cam_id, batch_id)
            self.cb_draw_graph_prob(self.dataframe_d, cam_id)
    
    def flt(self, pred_list): # make data frame recursive flat ndarray to list
        nparray = np.array(pred_list)
        # flat np array to list
        if nparray.shape == (config.BATCH_SIZE,):
            return list(nparray)
        else:
            nparray = np.array(list(itertools.chain(*nparray)))
            return self.flt(nparray)

