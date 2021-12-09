'1,3d' # delete title
'/-----/,/----/d' # delete start notes
's/《[^》]*》//g' # remove brackets
'/底本：/,$d' # remove end notes